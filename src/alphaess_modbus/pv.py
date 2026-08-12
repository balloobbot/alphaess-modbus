"""PV strings (0x41D - 0x428)."""

from __future__ import annotations

from modbus_connection.model import gauge, int32

from .component import AlphaESSComponent
from .variants import Variant


class PV(AlphaESSComponent):
    """The MPPT inputs; the third string exists on 3-MPPT inverters only."""

    voltage_1 = gauge(0x41D, 0.1, signed=False, unit="V")
    current_1 = gauge(0x41E, 0.1, signed=False, unit="A")
    power_1 = int32(0x41F, unit="W")
    voltage_2 = gauge(0x421, 0.1, signed=False, unit="V")
    current_2 = gauge(0x422, 0.1, signed=False, unit="A")
    power_2 = int32(0x423, unit="W")
    voltage_3 = gauge(0x425, 0.1, signed=False, unit="V")
    current_3 = gauge(0x426, 0.1, signed=False, unit="A")
    power_3 = int32(0x427, unit="W")

    field_variants = {
        "voltage_1": Variant.GEN,
        "current_1": Variant.GEN,
        "power_1": Variant.GEN,
        "voltage_2": Variant.GEN,
        "current_2": Variant.GEN,
        "power_2": Variant.GEN,
        "voltage_3": Variant.GEN | Variant.MPPT3,
        "current_3": Variant.GEN | Variant.MPPT3,
        "power_3": Variant.GEN | Variant.MPPT3,
    }
