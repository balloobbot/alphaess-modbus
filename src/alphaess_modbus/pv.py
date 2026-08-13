"""PV strings (0x41D - 0x428)."""

from __future__ import annotations

from modbus_connection.model import gauge, integer, uint32

from .component import AlphaESSComponent
from .variants import Variant


class PV(AlphaESSComponent):
    """The MPPT inputs, PV metering and capacity settings."""

    meter_ct_enable = integer(0x0080, signed=False)
    meter_ct_rate = integer(0x0081, signed=False)
    voltage_l1 = integer(0x0094, signed=False, unit="V")
    voltage_l2 = integer(0x0095, signed=False, unit="V")
    voltage_l3 = integer(0x0096, signed=False, unit="V")
    current_l1 = gauge(0x0097, 0.1, signed=False, unit="A")
    current_l2 = gauge(0x0098, 0.1, signed=False, unit="A")
    current_l3 = gauge(0x0099, 0.1, signed=False, unit="A")
    voltage_1 = gauge(0x41D, 0.1, signed=False, unit="V")
    current_1 = gauge(0x41E, 0.1, signed=False, unit="A")
    power_1 = uint32(0x41F, unit="W")
    voltage_2 = gauge(0x421, 0.1, signed=False, unit="V")
    current_2 = gauge(0x422, 0.1, signed=False, unit="A")
    power_2 = uint32(0x423, unit="W")
    voltage_3 = gauge(0x425, 0.1, signed=False, unit="V")
    current_3 = gauge(0x426, 0.1, signed=False, unit="A")
    power_3 = uint32(0x427, unit="W")
    voltage_4 = gauge(0x429, 0.1, signed=False, unit="V")
    current_4 = gauge(0x42A, 0.1, signed=False, unit="A")
    power_4 = uint32(0x42B, unit="W")

    total_power = uint32(0x453, unit="W")
    total_energy_from_pv = uint32(0x043E, scale=0.1, unit="kWh")
    max_feed_to_grid = uint32(0x0800, writable=True, unit="W")
    capacity_storage = uint32(0x0801, unit="W")
    pv_capacity_grid_inverter = uint32(0x0803, writable=True, unit="W")
    set_pv_power = integer(0x100A, signed=False, unit="W", writable=True)

    field_variants = {
        "meter_ct_enable": Variant.GEN,
        "meter_ct_rate": Variant.GEN,
        "voltage_l1": Variant.GEN | Variant.X3,
        "voltage_l2": Variant.GEN | Variant.X3,
        "voltage_l3": Variant.GEN | Variant.X3,
        "current_l1": Variant.GEN | Variant.X3,
        "current_l2": Variant.GEN | Variant.X3,
        "current_l3": Variant.GEN | Variant.X3,
        "voltage_1": Variant.GEN,
        "current_1": Variant.GEN,
        "power_1": Variant.GEN,
        "voltage_2": Variant.GEN,
        "current_2": Variant.GEN,
        "power_2": Variant.GEN,
        "voltage_3": Variant.GEN | Variant.MPPT3,
        "current_3": Variant.GEN | Variant.MPPT3,
        "power_3": Variant.GEN | Variant.MPPT3,
        "voltage_4": Variant.GEN | Variant.MPPT4,
        "current_4": Variant.GEN | Variant.MPPT4,
        "power_4": Variant.GEN | Variant.MPPT4,
        "total_power": Variant.GEN,
        "total_energy_from_pv": Variant.GEN,
        "max_feed_to_grid": Variant.GEN,
        "capacity_storage": Variant.GEN,
        "pv_capacity_grid_inverter": Variant.GEN,
        "set_pv_power": Variant.GEN,
    }
