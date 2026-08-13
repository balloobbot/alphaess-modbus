"""Battery measurements (0x100 - 0x123)."""

from __future__ import annotations

from modbus_connection.model import gauge, integer, uint32

from .component import AlphaESSComponent
from .variants import Variant


class Battery(AlphaESSComponent):
    """State of charge, capacity, telemetry and lifetime energy of the battery."""

    voltage = gauge(0x100, 0.1, unit="V")
    current = gauge(0x101, 0.1, unit="A")
    soc = integer(0x102, signed=False, unit="%")
    status = integer(0x103, signed=False)
    relay_status = integer(0x104, signed=False)
    min_cell_voltage = gauge(0x107, 0.001, signed=False, unit="V")
    max_cell_voltage = gauge(0x10A, 0.001, signed=False, unit="V")
    min_cell_temp = gauge(0x10D, 0.1, signed=True, unit="°C")
    max_cell_temp = gauge(0x110, 0.1, signed=True, unit="°C")
    max_charge_current = gauge(0x111, 0.1, signed=False, unit="A")
    max_discharge_current = gauge(0x112, 0.1, signed=False, unit="A")
    charge_cutoff_voltage = gauge(0x113, 0.1, signed=False, unit="V")
    discharge_cutoff_voltage = gauge(0x114, 0.1, signed=False, unit="V")
    bmu_software_version = integer(0x115, signed=False)
    lmu_software_version = integer(0x116, signed=False)
    iso_software_version = integer(0x117, signed=False)
    battery_module_count = integer(0x118, signed=False)
    capacity = gauge(0x119, 0.1, signed=False, unit="kWh")
    battery_type = integer(0x11A, signed=False)
    soh = gauge(0x11B, 0.1, signed=False, unit="%")
    battery_warning = uint32(0x11C)
    battery_fault = uint32(0x11E)
    input_energy = uint32(0x120, scale=0.1, unit="kWh")
    """Lifetime energy charged into the battery."""
    output_energy = uint32(0x122, scale=0.1, unit="kWh")
    """Lifetime energy discharged from the battery."""
    total_energy_charge_from_grid = uint32(0x124, scale=0.1, unit="kWh")
    power = integer(0x126, signed=True, unit="W")
    remaining_time_raw = integer(0x127, signed=False, unit="min")
    battery_1_fault = uint32(0x131)
    battery_2_fault = uint32(0x133)
    battery_3_fault = uint32(0x135)
    battery_4_fault = uint32(0x137)
    battery_5_fault = uint32(0x139)
    battery_6_fault = uint32(0x13B)
    battery_1_warning = uint32(0x13D)
    battery_2_warning = uint32(0x13F)
    battery_3_warning = uint32(0x141)
    battery_4_warning = uint32(0x143)
    battery_5_warning = uint32(0x145)
    battery_6_warning = uint32(0x147)

    field_variants = {
        "voltage": Variant.GEN,
        "current": Variant.HYBRID | Variant.GEN2,
        "soc": Variant.GEN,
        "status": Variant.GEN,
        "relay_status": Variant.GEN,
        "min_cell_voltage": Variant.GEN,
        "max_cell_voltage": Variant.GEN,
        "min_cell_temp": Variant.GEN,
        "max_cell_temp": Variant.GEN,
        "max_charge_current": Variant.GEN,
        "max_discharge_current": Variant.GEN,
        "charge_cutoff_voltage": Variant.GEN,
        "discharge_cutoff_voltage": Variant.GEN,
        "bmu_software_version": Variant.GEN,
        "lmu_software_version": Variant.GEN,
        "iso_software_version": Variant.GEN,
        "battery_module_count": Variant.GEN,
        "capacity": Variant.GEN,
        "battery_type": Variant.GEN,
        "soh": Variant.GEN,
        "battery_warning": Variant.GEN,
        "battery_fault": Variant.GEN,
        "input_energy": Variant.GEN,
        "output_energy": Variant.GEN,
        "total_energy_charge_from_grid": Variant.GEN,
        "power": Variant.GEN,
        "remaining_time_raw": Variant.GEN,
        "battery_1_fault": Variant.GEN,
        "battery_2_fault": Variant.GEN,
        "battery_3_fault": Variant.GEN,
        "battery_4_fault": Variant.GEN,
        "battery_5_fault": Variant.GEN,
        "battery_6_fault": Variant.GEN,
        "battery_1_warning": Variant.GEN,
        "battery_2_warning": Variant.GEN,
        "battery_3_warning": Variant.GEN,
        "battery_4_warning": Variant.GEN,
        "battery_5_warning": Variant.GEN,
        "battery_6_warning": Variant.GEN,
    }
