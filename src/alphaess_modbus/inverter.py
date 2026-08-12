"""Inverter output, temperature and run mode (0x400 - 0x440)."""

from __future__ import annotations

from modbus_connection.model import enum, gauge, int32, integer

from .component import AlphaESSComponent
from .enums import RunMode
from .variants import Variant


class Inverter(AlphaESSComponent):
    """The inverter's own AC output, plus its temperature and run mode."""

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
    run_mode = enum(0x440, RunMode)

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
        "run_mode": Variant.GEN,
    }
