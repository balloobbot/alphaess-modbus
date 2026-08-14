"""What a poll actually asks the device for."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from alphaess_modbus import AlphaESS, AlphaESSComponent, Variant


def _blocks(unit: MockModbusUnit) -> list[tuple[int, int]]:
    return [(event.address, event.count) for event in unit.read_events]


def _covered(unit: MockModbusUnit) -> set[int]:
    return {
        address
        for event in unit.read_events
        for address in range(event.address, event.address + event.count)
    }


def _kept_addresses(component: AlphaESSComponent) -> set[int]:
    return {
        address
        for resolved in component.resolved_fields.values()
        for address in range(resolved.address, resolved.address + resolved.count)
    }


def _dropped_addresses(component: AlphaESSComponent) -> set[int]:
    kept = set(component.resolved_fields)
    dropped = {
        address
        for name, field in component.declared_fields.items()
        if name not in kept
        for address in range(field.address, field.address + field.count)
    }
    # A dropped field may share a register with a kept one (the X1/X3 pairs).
    return dropped - _kept_addresses(component)


def _components(device: AlphaESS) -> list[AlphaESSComponent]:
    components = [
        device.info,
        device.grid,
        device.battery,
        device.inverter,
        device.eps,
        device.pv,
        device.settings,
    ]
    return [component for component in components if component.has_fields]


@pytest.mark.parametrize(
    "variant",
    [
        Variant.GEN,
        Variant.GEN | Variant.X1,
        Variant.GEN | Variant.X3 | Variant.EPS | Variant.MPPT3,
        Variant.MAX | Variant.GEN2 | Variant.MPPT5,
    ],
)
async def test_poll_covers_every_field(unit: MockModbusUnit, variant: Variant) -> None:
    device = AlphaESS(unit, variant)
    await device.async_update()
    covered = _covered(unit)
    for component in _components(device):
        assert _kept_addresses(component) <= covered


@pytest.mark.parametrize("variant", [Variant.GEN, Variant.GEN | Variant.X1])
async def test_a_component_never_reads_a_register_it_dropped(
    unit: MockModbusUnit, variant: Variant
) -> None:
    """Registers of fields this variant lacks stay out of that component's reads.

    A block does widen over a gap another component fills — the inverter reads
    across the EPS registers — but never over a register this variant dropped.
    """
    device = AlphaESS(unit, variant)
    for component in _components(device):
        unit.read_events.clear()
        await component.async_update()
        assert not _dropped_addresses(component) & _covered(unit)


async def test_reads_are_holding_registers_within_the_block_limit(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    await device.async_update()
    assert unit.read_events
    for event in unit.read_events:
        assert event.register_type == "holding"
        assert event.count <= AlphaESSComponent.max_span  # upstream's block size


async def test_block_pattern_three_phase(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    await device.async_update()
    assert _blocks(unit) == [
        (0x640, 20),  # identity: versions + serial number, read once
        (0x014, 15),  # grid 0x14-0x22
        (0x100, 1),  # battery voltage
        (0x102, 1),  # battery SOC (0x101 belongs to a field this variant lacks)
        (0x119, 11),  # battery capacity + lifetime energy
        (0x400, 29),  # inverter output 0x400-0x40D + frequency 0x41C, over the
        (0x435, 12),  # EPS gap; temperature + run mode
        (0x40E, 14),  # EPS, re-reading what the inverter block covered
        (0x41D, 12),  # PV 1-3
        (0x805, 13),  # system mode + unbalance mode
        (0x84F, 19),  # time period control + the charge/discharge schedule
    ]


async def test_block_pattern_unknown_gen(unit: MockModbusUnit) -> None:
    device = AlphaESS(unit, Variant.GEN)
    await device.async_update()
    assert _blocks(unit) == [
        (0x640, 20),
        (0x01A, 9),  # grid frequency + active power only
        (0x100, 1),
        (0x102, 1),
        (0x119, 11),
        (0x40C, 17),  # inverter power + frequency; no per-phase fields
        (0x435, 12),
        # EPS has no fields for this variant, so nothing re-reads 0x40E-0x41B.
        (0x41D, 8),  # PV 1 and 2
        (0x805, 1),  # no unbalance mode without X3
        (0x84F, 19),
    ]


async def test_identity_is_read_once(unit: MockModbusUnit, device: AlphaESS) -> None:
    await device.async_update()
    unit.read_events.clear()
    await device.async_update()
    assert (0x640, 20) not in _blocks(unit)
    assert len(_blocks(unit)) == 10


@pytest.mark.parametrize(
    "variant",
    [
        Variant.GEN,
        Variant.GEN | Variant.X1,
        Variant.GEN | Variant.X3 | Variant.EPS | Variant.MPPT3,
        Variant.MAX | Variant.GEN2 | Variant.MPPT5,
    ],
)
async def test_read_raw_covers_every_field(
    unit: MockModbusUnit, variant: Variant
) -> None:
    """A dump an issue report can use needs identity too, not just the poll."""
    device = AlphaESS(unit, variant)
    dumped = set((await device.async_read_raw())["holding"])
    for component in _components(device):
        assert _kept_addresses(component) <= dumped


async def test_read_raw_still_covers_identity_once_the_poll_drops_it(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    await device.async_update()  # identity read, and out of the poll from here

    raw = await device.async_read_raw()

    assert set(raw) == {"holding"}
    assert _kept_addresses(device.info) <= set(raw["holding"])


async def test_read_raw_refreshes_without_notifying(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    """A download writes no state: it is not a poll, however fresh its values."""
    await device.async_update()
    fired: list[int] = []
    for component in _components(device):
        component.add_update_listener(lambda: fired.append(1))

    unit.holding[0x41C] = 4990  # inverter frequency changes on the device
    await device.async_read_raw()

    assert not fired
    assert device.inverter.frequency == 49.9  # the fields still refreshed
