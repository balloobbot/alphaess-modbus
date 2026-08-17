"""One failing block must not take the rest of the poll with it.

Upstream reads this device in independent blocks and tolerates a failure
(``auto_block_ignore_readerror=True``): the failing block's sensors keep their
last values while everything else refreshes. The library mirrors that at
component granularity.
"""

from __future__ import annotations

from collections import Counter

import pytest
from modbus_connection import ModbusConnectionError, ModbusTimeoutError
from modbus_connection.mock import MockModbusUnit

from alphaess_modbus import AlphaESS


async def test_a_failed_component_leaves_the_rest_fresh(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    await device.async_update()
    before = device.inverter.frequency

    unit.holding[0x41C] = 4990  # inverter frequency changes on the device
    unit.holding[0x102] = 50  # so does battery SOC
    unit.holding[0x41A] = [0, 400]  # and EPS power
    unit.fail_read(0x400, ModbusTimeoutError("slow inverter block"))
    report = await device.async_update()

    assert not report.complete
    assert set(report.failed) == {"inverter"}
    assert isinstance(report.failed["inverter"], ModbusTimeoutError)
    assert device.inverter.frequency == before

    # EPS lives inside the inverter's block span but reads for itself, so the
    # inverter's failure does not reach it.
    assert {"battery", "eps"} <= report.updated
    assert device.battery.soc == 50
    assert device.eps.power == 400


async def test_listeners_fire_at_the_end_and_only_for_fresh_components(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    await device.async_update()
    seen: list[int] = []
    device.battery.add_update_listener(lambda: seen.append(len(unit.read_events)))
    device.inverter.add_update_listener(lambda: seen.append(-1))

    unit.fail_read(0x400, ModbusTimeoutError("slow inverter block"))
    unit.read_events.clear()
    await device.async_update()

    # One notification, after every component was tried; none for the failure.
    assert seen == [len(unit.read_events)]


async def test_a_settings_poll_notifies_its_own_sub_systems(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    """Polling settings alone fires their listeners, and only theirs."""
    await device.async_update()
    seen: list[str] = []
    device.settings.add_update_listener(lambda: seen.append("settings"))
    device.battery.add_update_listener(lambda: seen.append("battery"))

    await device.async_update_settings()

    assert seen == ["settings"]


async def test_a_full_poll_notifies_each_component_once(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    """One cycle is one notification, whichever phase refreshed the component."""
    await device.async_update()
    counts: Counter[str] = Counter()
    device.battery.add_update_listener(lambda: counts.update(["battery"]))
    device.settings.add_update_listener(lambda: counts.update(["settings"]))

    await device.async_update()

    assert counts["battery"] == 1
    assert counts["settings"] == 1


async def test_a_dead_link_raises_instead_of_reporting(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    await device.async_update()
    unit.fail_requests(ModbusConnectionError("link down"))
    with pytest.raises(ModbusConnectionError):
        await device.async_update()


async def test_every_component_refreshes_on_a_healthy_device(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    report = await device.async_update()
    assert report.complete
    assert report.failed == {}
    assert report.updated == {
        "info",
        "grid",
        "battery",
        "inverter",
        "eps",
        "pv",
        "settings",
    }


async def test_a_timeout_before_anything_answered_is_fatal(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    """A silent inverter: the rest would only pay a full timeout each."""
    unit.fail_read(0x14, ModbusTimeoutError("inverter asleep"))
    unit.read_events.clear()

    with pytest.raises(ModbusTimeoutError):
        await device.async_update()

    assert len(unit.read_events) == 1  # the poll stopped at the first block


async def test_a_settings_poll_of_a_silent_device_is_fatal_too(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    """Nothing has answered this cycle either, so the same rule applies."""
    await device.async_update()
    unit.fail_read(0x805, ModbusTimeoutError("inverter asleep"))
    unit.read_events.clear()

    with pytest.raises(ModbusTimeoutError):
        await device.async_update_settings()

    assert len(unit.read_events) == 1


async def test_a_settings_failure_within_a_full_poll_is_contained(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    """The readings answered, so the settings timeout only costs the settings."""
    await device.async_update()
    unit.fail_read(0x805, ModbusTimeoutError("slow settings block"))

    report = await device.async_update()

    assert set(report.failed) == {"settings"}
    assert "battery" in report.updated


async def test_a_failed_identity_read_is_contained_and_retried(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    """Identity is read once, but a transient failure must not cost the poll.

    It is polled last for exactly this reason: leading with it would make a
    slow identity block fatal to a device that is answering everywhere else.
    """
    unit.fail_read(0x640, ModbusTimeoutError("slow identity block"))
    report = await device.async_update()

    assert set(report.failed) == {"info"}
    assert device.info.serial_number is None
    assert device.battery.soc == 87  # the rest of the first poll still landed

    unit.fail_read(0x640, None)
    report = await device.async_update()

    assert report.complete
    assert "info" in report.updated
    assert device.info.serial_number == "XYZ12345678901234567"


async def test_identity_stops_being_polled_once_it_lands(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    await device.async_update()
    report = await device.async_update()
    assert "info" not in report.updated


async def test_a_failed_detection_leaves_no_device_behind(
    unit: MockModbusUnit,
) -> None:
    """Detection is the only setup read, and it builds the device or nothing."""
    unit.fail_read(0x64A, ModbusTimeoutError("no serial"))
    with pytest.raises(ModbusTimeoutError):
        await AlphaESS.async_detect(unit)
