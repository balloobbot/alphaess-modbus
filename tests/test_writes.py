"""Writable settings, their validators and what the device sees."""

from __future__ import annotations

import pytest
from modbus_connection import IllegalDataValueError
from modbus_connection.mock import MockModbusUnit, WriteEvent

from alphaess_modbus import AlphaESS, SystemMode, TimePeriodControl, Variant


async def test_write_system_mode(unit: MockModbusUnit, device: AlphaESS) -> None:
    await device.settings.write("system_mode", SystemMode.DC)
    assert unit.holding[0x805] == 1
    await device.settings.async_update()
    assert device.settings.system_mode is SystemMode.DC


async def test_write_time_period_control(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    await device.settings.write("time_period_control", TimePeriodControl.CHARGE_ENABLED)
    assert unit.holding[0x84F] == 1


async def test_write_unbalance_mode(unit: MockModbusUnit, device: AlphaESS) -> None:
    await device.settings.write("three_phase_unbalance_mode", False)
    assert unit.holding[0x811] == 0


async def test_write_schedule(unit: MockModbusUnit, device: AlphaESS) -> None:
    await device.settings.write("charge_start_1_hours", 23)
    await device.settings.write("charge_start_1_mins", 59)
    await device.settings.write("charge_target_soc", 90)
    assert unit.holding[0x856] == 23
    assert unit.holding[0x85E] == 59
    assert unit.holding[0x855] == 90


async def test_writes_use_fc06(unit: MockModbusUnit, device: AlphaESS) -> None:
    seen: list[WriteEvent] = []
    unit.on_write(seen.append)
    await device.settings.write("discharge_minimum_soc", 15)
    assert [(e.address, e.values, e.function_code) for e in seen] == [
        (0x850, [15], 0x06)
    ]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("charge_target_soc", 100),
        ("charge_target_soc", 9),
        ("discharge_minimum_soc", 0),
        ("charge_start_1_hours", 24),
        ("discharge_stop_2_hours", -1),
        ("charge_stop_2_mins", 60),
    ],
)
async def test_out_of_range_write_is_refused(
    unit: MockModbusUnit, device: AlphaESS, field: str, value: int
) -> None:
    before = dict(unit.holding)
    with pytest.raises(ValueError):
        await device.settings.write(field, value)
    assert unit.holding == before


async def test_measurements_are_read_only(device: AlphaESS) -> None:
    with pytest.raises(AttributeError):
        await device.battery.write("soc", 50)


async def test_a_field_this_variant_lacks_cannot_be_written(
    unit: MockModbusUnit,
) -> None:
    device = AlphaESS(unit, Variant.GEN | Variant.X1)
    with pytest.raises(AttributeError):
        await device.settings.write("three_phase_unbalance_mode", True)


async def test_a_rejected_write_leaves_the_register_alone(
    unit: MockModbusUnit, device: AlphaESS
) -> None:
    unit.fail_write(0x855, IllegalDataValueError())
    with pytest.raises(IllegalDataValueError):
        await device.settings.write("charge_target_soc", 50)
    assert unit.holding[0x855] == 95
