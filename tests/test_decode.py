"""Decoding: scales, signedness, 32-bit values, strings and enums."""

from __future__ import annotations

from datetime import datetime

import pytest
from modbus_connection.mock import MockModbusUnit

from alphaess_modbus import (
    AlphaESS,
    Battery,
    DispatchMode,
    Grid,
    RunMode,
    SystemMode,
    TimePeriodControl,
    Variant,
)


async def test_grid(device: AlphaESS) -> None:
    await device.async_update()
    grid = device.grid
    assert grid.voltage_l1 == 230
    assert grid.voltage_l2 == 231
    assert grid.voltage_l3 == 229
    assert grid.current_l1 == pytest.approx(10.5)
    assert grid.current_l2 == pytest.approx(11.0)
    assert grid.current_l3 == pytest.approx(9.8)
    assert grid.frequency == pytest.approx(49.98)
    assert grid.active_power_energy == -3500  # int32, negative
    assert grid.voltage is None  # single-phase field on a three-phase inverter


async def test_single_phase_shares_the_three_phase_registers(
    unit: MockModbusUnit,
) -> None:
    device = AlphaESS(unit, Variant.GEN | Variant.X1)
    await device.async_update()
    assert device.grid.voltage == 230  # same register as voltage_l1
    assert device.grid.current == pytest.approx(10.5)
    assert device.inverter.voltage == 231
    assert device.eps.voltage == 228
    assert device.grid.voltage_l1 is None


async def test_battery(device: AlphaESS) -> None:
    await device.async_update()
    assert device.battery is not None
    battery = device.battery
    assert battery.voltage == pytest.approx(51.2)
    assert battery.soc == 87
    assert battery.bmu_software_version == 104
    assert battery.capacity == pytest.approx(13.2)
    assert battery.input_energy == pytest.approx(10000.0)  # uint32 * 0.1
    assert battery.output_energy == pytest.approx(3000.0)
    assert battery.current is None  # HYBRID | GEN2 only


async def test_battery_current_is_signed(unit: MockModbusUnit) -> None:
    battery = Battery(unit, Variant.HYBRID | Variant.GEN2)
    await battery.async_update()
    assert battery.current == pytest.approx(-2.0)  # int16


async def test_reactive_power(unit: MockModbusUnit) -> None:
    grid = Grid(unit, Variant.MAX | Variant.GEN2)
    await grid.async_update()
    assert grid.reactive_power == 1200
    assert grid.frequency is None  # GEN only


async def test_inverter(device: AlphaESS) -> None:
    await device.async_update()
    inverter = device.inverter
    assert inverter.voltage_l1 == 231
    assert inverter.current_l1 == pytest.approx(10.0)
    assert inverter.power_l1 == 700
    assert inverter.power_l2 == 720
    assert inverter.power_l3 == -700
    assert inverter.power == 2140
    assert inverter.frequency == pytest.approx(50.01)
    assert inverter.temperature == pytest.approx(35.2)
    assert inverter.run_mode is RunMode.ONLINE
    assert inverter.dispatch_mode is DispatchMode.SOC_CONTROL
    assert inverter.system_time == datetime(2026, 5, 13, 7, 47, 12)


async def test_eps(device: AlphaESS) -> None:
    await device.async_update()
    eps = device.eps
    assert eps.voltage_l1 == 228
    assert eps.voltage_l3 == 226
    assert eps.current_l3 == pytest.approx(0.7)
    assert eps.power_l1 == 120
    assert eps.power == 390


async def test_pv(device: AlphaESS) -> None:
    await device.async_update()
    pv = device.pv
    assert pv.voltage_1 == pytest.approx(300.5)
    assert pv.current_1 == pytest.approx(5.2)
    assert pv.power_1 == 1560
    assert pv.voltage_2 == pytest.approx(298.0)
    assert pv.power_2 == 1430
    assert pv.voltage_3 == pytest.approx(150.0)
    assert pv.power_3 == 300


async def test_pv_third_string_needs_mppt3(unit: MockModbusUnit) -> None:
    device = AlphaESS(unit, Variant.GEN)
    await device.async_update()
    assert device.pv.power_2 == 1430
    assert device.pv.voltage_3 is None
    assert device.pv.power_3 is None


async def test_identity(device: AlphaESS) -> None:
    await device.async_update()
    assert device.info.serial_number == "XYZ12345678901234567"
    assert device.info.software_master_version == "V1.23"
    # Upstream reads 8 registers for the slave version, three of which are the
    # first characters of the serial number at 0x64A.
    assert device.info.software_slave_version == "SLAVE-2.34XYZ123"
    assert device.info.ems_version == "1.0.23"
    assert device.info.ems_serial_number == "EMS1234567890123"


async def test_network(device: AlphaESS) -> None:
    from ipaddress import IPv4Address

    from alphaess_modbus import IpMethod

    await device.async_update()
    assert device.network.ip_method is IpMethod.DHCP
    assert device.network.local_ip == IPv4Address("10.0.0.209")
    assert device.network.subnet_mask == IPv4Address("255.255.255.0")
    assert device.network.gateway == IPv4Address("10.0.0.1")
    assert device.network.modbus_baud_rate == 9600


async def test_settings(device: AlphaESS) -> None:
    await device.async_update()
    settings = device.settings
    assert settings.system_mode is SystemMode.HYBRID
    assert settings.three_phase_unbalance_mode is True
    assert settings.time_period_control is TimePeriodControl.BOTH_ENABLED
    assert settings.discharge_minimum_soc == 20
    assert settings.charge_target_soc == 95
    assert settings.charge_start_1_hours == 2
    assert settings.charge_start_1_mins == 10
    assert settings.discharge_stop_2_hours == 16
    assert settings.discharge_stop_2_mins == 15


async def test_unbalance_mode_is_three_phase_only(unit: MockModbusUnit) -> None:
    device = AlphaESS(unit, Variant.GEN | Variant.X1)
    await device.async_update()
    assert device.settings.three_phase_unbalance_mode is None


async def test_unknown_run_mode_decodes_to_none(unit: MockModbusUnit) -> None:
    unit.holding[0x440] = 99
    device = AlphaESS(unit, Variant.GEN)
    await device.async_update()
    assert device.inverter.run_mode is None


async def test_bmu(device: AlphaESS) -> None:
    await device.async_update()
    bmu = device.bmu
    assert bmu is not None
    assert bmu.soc == 92
    assert len(device.bmu_modules) == 1
    assert device.bmu_modules[0].soc == 95
    assert device.bmu_modules[0].cluster_voltage == pytest.approx(52.0)
