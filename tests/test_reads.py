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
    return [device.info, *device.polled_components]


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

    Pooling several components into one poll does widen a block over another
    component's gap — as upstream's 100-register blocks do — but a component
    refreshed on its own reads only what it kept.
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
    # On setup (first update), identity, battery, bmu and bmu_module candidates
    # are probed individually, followed by the pooled group poll.
    group_blocks = [
        (0x000, 35),  # grid & PV CT meters + energy totals + voltages/currents/powers
        (0x080, 2),  # PV meter CT
        (0x090, 19),  # PV energy + PV phase voltages/currents + PV meter power
        (0x100, 1),  # battery voltage
        (0x102, 71),  # battery SOC + telemetry + alarms + energy + power
        (0x400, 29),  # inverter + EPS
        (0x41D, 12),  # PV string measurements
        (0x435, 9),  # temperature + run mode + warnings/faults
        (0x43E, 2),  # total energy from PV
        (0x440, 1),  # run mode
        (0x453, 2),  # total PV power
        (0x740, 3),  # RTC system time
        (0x800, 5),  # PV capacity settings
        (0x805, 13),  # system mode + unbalance mode
        (0x84F, 19),  # time period control + schedule
        (0x880, 18),  # dispatch control block
        (0x8D4, 2),  # system fault
        (0x1000, 37),  # grid regulation + safety mode + protection setpoints
        (0x1100, 15),  # reset mode + system language
        (0xA000, 30),  # top BMU summary
        (0xA200, 41),  # BMU module 1
    ]
    assert _blocks(unit) == [
        (0x640, 20),  # identity master/slave/sn
        (0x743, 11),  # EMS serial number + version
        (0x100, 1),  # battery probe 1
        (0x102, 71),  # battery probe 2
        (0xA000, 30),  # top BMU probe
        (0xA200, 41),  # BMU module 1 probe
        (0xA300, 41),  # BMU module 2 probe (returns 0 sn, stopping probe)
        *group_blocks,
    ]


async def test_block_pattern_unknown_gen(unit: MockModbusUnit) -> None:
    device = AlphaESS(unit, Variant.GEN)
    await device.async_update()
    group_blocks = [
        (0x000, 20),
        (0x01A, 1),
        (0x021, 2),
        (0x080, 2),
        (0x090, 19),
        (0x100, 1),
        (0x102, 71),
        (0x40C, 25),
        (0x435, 12),
        (0x453, 2),
        (0x740, 3),
        (0x800, 6),
        (0x808, 9),
        (0x84F, 19),
        (0x880, 18),
        (0x8D4, 2),
        (0x1000, 27),
        (0x1100, 15),
        (0xA000, 30),
        (0xA200, 41),
    ]
    assert _blocks(unit) == [
        (0x640, 20),
        (0x743, 11),
        (0x100, 1),
        (0x102, 71),
        (0xA000, 30),
        (0xA200, 41),
        (0xA300, 41),
        *group_blocks,
    ]


async def test_identity_is_read_once(unit: MockModbusUnit, device: AlphaESS) -> None:
    await device.async_update()
    unit.read_events.clear()
    await device.async_update()
    assert (0x640, 20) not in _blocks(unit)
    assert len(_blocks(unit)) == 21


async def test_no_battery_installation(unit: MockModbusUnit) -> None:
    """When battery/BMU fail with IllegalDataAddressError, attributes are None."""
    from modbus_connection import IllegalDataAddressError

    unit.fail_read(0x100, IllegalDataAddressError(2))
    unit.fail_read(0xA000, IllegalDataAddressError(2))

    device = AlphaESS(unit, Variant.GEN)
    await device.async_update()
    assert device.battery is None
    assert device.bmu is None
    assert device.bmu_modules == []


async def test_multiple_bmu_modules_probing(unit: MockModbusUnit) -> None:
    """Probing finds multiple BMU modules until a sentinel is encountered."""
    # Seed module 1 (0xA200), module 2 (0xA300), and module 3 (0xA400)
    unit.holding[0xA200] = [0x0001, 0x0001]  # sn = 65537
    unit.holding[0xA300] = [0x0001, 0x0002]  # sn = 65538
    unit.holding[0xA400] = [0x0000, 0x0000]  # sn = 0 (sentinel)

    device = AlphaESS(unit, Variant.GEN)
    await device.async_update()
    assert len(device.bmu_modules) == 2
    assert device.bmu_modules[0].sn == 65537
    assert device.bmu_modules[1].sn == 65538


async def test_bmu_sentinel_ffff_ffff(unit: MockModbusUnit) -> None:
    """A BMU module returning 0xFFFFFFFF for serial number is treated as missing."""
    unit.holding[0xA200] = [0xFFFF, 0xFFFF]  # sn = 0xFFFFFFFF (sentinel)

    device = AlphaESS(unit, Variant.GEN)
    await device.async_update()
    assert len(device.bmu_modules) == 0

