"""Battery measurements (0x100 - 0x123)."""

from __future__ import annotations

from modbus_connection.model import gauge, integer, uint32

from .component import AlphaESSComponent
from .variants import Variant


class Battery(AlphaESSComponent):
    """State of charge, capacity and lifetime energy of the battery."""

    voltage = gauge(0x100, 0.1, unit="V")
    current = gauge(0x101, 0.1, unit="A")
    soc = integer(0x102, signed=False, unit="%")
    capacity = gauge(0x119, 0.1, signed=False, unit="kWh")
    input_energy = uint32(0x120, scale=0.1, unit="kWh")
    """Lifetime energy charged into the battery."""
    output_energy = uint32(0x122, scale=0.1, unit="kWh")
    """Lifetime energy discharged from the battery."""

    field_variants = {
        "voltage": Variant.GEN,
        "current": Variant.HYBRID | Variant.GEN2,
        "soc": Variant.GEN,
        "capacity": Variant.GEN,
        "input_energy": Variant.GEN,
        "output_energy": Variant.GEN,
    }
