"""Inverter output, temperature and run mode (0x400 - 0x440)."""

from __future__ import annotations

from modbus_connection.model import enum, gauge, int32, integer, uint32

from .component import AlphaESSComponent
from .enums import DispatchMode, ResetMode, RunMode
from .fields import rtc
from .variants import Variant


class Inverter(AlphaESSComponent):
    """The inverter's AC output, temperature, run mode and system controls."""

    voltage = integer(0x400, signed=False, unit="V")
    voltage_l1 = integer(0x400, signed=False, unit="V")
    voltage_l2 = integer(0x401, signed=False, unit="V")
    voltage_l3 = integer(0x402, signed=False, unit="V")
    current = gauge(0x403, 0.1, signed=False, unit="A")
    current_l1 = gauge(0x403, 0.1, signed=False, unit="A")
    current_l2 = gauge(0x404, 0.1, signed=False, unit="A")
    current_l3 = gauge(0x405, 0.1, signed=False, unit="A")
    power_l1 = int32(0x406, unit="W")
    power_l2 = int32(0x408, unit="W")
    power_l3 = int32(0x40A, unit="W")
    power = int32(0x40C, unit="W")
    frequency = gauge(0x41C, 0.01, signed=False, unit="Hz")
    temperature = gauge(0x435, 0.1, signed=False, unit="°C")
    warning_1 = uint32(0x436)
    warning_2 = uint32(0x438)
    fault_1 = uint32(0x43A)
    fault_2 = uint32(0x43C)
    run_mode = enum(0x440, RunMode)
    system_time = rtc(0x0740, writable=True)
    dispatch_mode = enum(0x0885, DispatchMode)
    system_fault = uint32(0x08D4)
    safety_mode_enable = uint32(0x1002)
    pf_value = gauge(0x1006, 0.01, signed=True)
    volt_watt_starting = gauge(0x1007, 0.1, signed=False, unit="V")
    reset_mode = enum(0x1100, ResetMode, writable=True)
    system_language = integer(0x110E, signed=False)

    field_variants = {
        "voltage": Variant.GEN | Variant.X1,
        "voltage_l1": Variant.GEN | Variant.X3,
        "voltage_l2": Variant.GEN | Variant.X3,
        "voltage_l3": Variant.GEN | Variant.X3,
        "current": Variant.GEN | Variant.X1,
        "current_l1": Variant.GEN | Variant.X3,
        "current_l2": Variant.GEN | Variant.X3,
        "current_l3": Variant.GEN | Variant.X3,
        "power_l1": Variant.GEN | Variant.X3,
        "power_l2": Variant.GEN | Variant.X3,
        "power_l3": Variant.GEN | Variant.X3,
        "power": Variant.GEN,
        "frequency": Variant.GEN,
        "temperature": Variant.GEN,
        "warning_1": Variant.GEN,
        "warning_2": Variant.GEN,
        "fault_1": Variant.GEN,
        "fault_2": Variant.GEN,
        "run_mode": Variant.GEN,
        "system_time": Variant.GEN,
        "dispatch_mode": Variant.GEN,
        "system_fault": Variant.GEN,
        "safety_mode_enable": Variant.GEN,
        "pf_value": Variant.GEN,
        "volt_watt_starting": Variant.GEN,
        "reset_mode": Variant.GEN,
        "system_language": Variant.GEN,
    }
