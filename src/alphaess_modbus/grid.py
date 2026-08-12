"""Grid-side measurements (0x14 - 0x2A)."""

from __future__ import annotations

from modbus_connection.model import gauge, int32, integer

from .component import AlphaESSComponent
from .variants import Variant


class Grid(AlphaESSComponent):
    """Voltage, current, frequency and power measured on the grid connection."""

    voltage = integer(0x14, signed=False, unit="V")
    voltage_l1 = integer(0x14, signed=False, unit="V")
    voltage_l2 = integer(0x15, signed=False, unit="V")
    voltage_l3 = integer(0x16, signed=False, unit="V")
    current = gauge(0x17, 0.1, signed=False, unit="A")
    current_l1 = gauge(0x17, 0.1, signed=False, unit="A")
    current_l2 = gauge(0x18, 0.1, signed=False, unit="A")
    current_l3 = gauge(0x19, 0.1, signed=False, unit="A")
    frequency = gauge(0x1A, 0.01, signed=False, unit="Hz")
    active_power_energy = int32(0x21, unit="W")
    """Active power on the grid connection (upstream name: Active Power Energy)."""
    reactive_power = int32(0x29, unit="var")

    field_variants = {
        "voltage": Variant.GEN | Variant.X1,
        "voltage_l1": Variant.GEN | Variant.X3,
        "voltage_l2": Variant.GEN | Variant.X3,
        "voltage_l3": Variant.GEN | Variant.X3,
        "current": Variant.GEN | Variant.X1,
        "current_l1": Variant.GEN | Variant.X3,
        "current_l2": Variant.GEN | Variant.X3,
        "current_l3": Variant.GEN | Variant.X3,
        "frequency": Variant.GEN,
        "active_power_energy": Variant.GEN,
        "reactive_power": Variant.MAX | Variant.GEN2,
    }
