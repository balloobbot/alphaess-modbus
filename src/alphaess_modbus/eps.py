"""Emergency power supply output (0x40E - 0x41B)."""

from __future__ import annotations

from modbus_connection.model import gauge, int32, integer

from .component import AlphaESSComponent
from .variants import Variant


class EPS(AlphaESSComponent):
    """The backup (EPS) output the inverter serves when the grid is down."""

    voltage = integer(0x40E, signed=False, unit="V")
    voltage_l1 = integer(0x40E, signed=False, unit="V")
    voltage_l2 = integer(0x40F, signed=False, unit="V")
    voltage_l3 = integer(0x410, signed=False, unit="V")
    current = gauge(0x411, 0.1, signed=False, unit="A")
    current_l1 = gauge(0x411, 0.1, signed=False, unit="A")
    current_l2 = gauge(0x412, 0.1, signed=False, unit="A")
    current_l3 = gauge(0x413, 0.1, signed=False, unit="A")
    power_l1 = int32(0x414, unit="W")
    power_l2 = int32(0x416, unit="W")
    power_l3 = int32(0x418, unit="W")
    power = int32(0x41A, unit="W")

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
        # The only field upstream gates on the EPS option; the rest come with
        # the phase count.
        "power": Variant.GEN | Variant.EPS,
    }
