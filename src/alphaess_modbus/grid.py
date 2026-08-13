"""Grid-side measurements (0x14 - 0x2A)."""

from __future__ import annotations

from modbus_connection.model import gauge, int32, integer, uint32

from .component import AlphaESSComponent
from .variants import Variant


class Grid(AlphaESSComponent):
    """Voltage, current, frequency and power measured on the grid connection."""

    grid_meter_ct_enable = integer(0x00, signed=False)
    grid_meter_ct_rate = integer(0x01, signed=False)
    total_energy_feed_to_grid = uint32(0x10, scale=0.01, unit="kWh")
    total_energy_consume_from_grid = uint32(0x12, scale=0.01, unit="kWh")
    voltage = integer(0x14, signed=False, unit="V")
    voltage_l1 = integer(0x14, signed=False, unit="V")
    voltage_l2 = integer(0x15, signed=False, unit="V")
    voltage_l3 = integer(0x16, signed=False, unit="V")
    current = gauge(0x17, 0.1, signed=False, unit="A")
    current_l1 = gauge(0x17, 0.1, signed=False, unit="A")
    current_l2 = gauge(0x18, 0.1, signed=False, unit="A")
    current_l3 = gauge(0x19, 0.1, signed=False, unit="A")
    frequency = gauge(0x1A, 0.01, signed=False, unit="Hz")
    power_l1 = int32(0x1B, unit="W")
    power_l2 = int32(0x1D, unit="W")
    power_l3 = int32(0x1F, unit="W")

    active_power_energy = int32(0x21, unit="W")
    """Active power on the grid connection (upstream name: Active Power Energy)."""
    reactive_power = int32(0x29, unit="var")
    total_energy_feed_to_grid_pv = uint32(0x90, scale=0.1, unit="kWh")
    active_power_pv_meter = int32(0xA1, unit="W")
    grid_regulation = integer(0x1000, signed=False)
    ovp_l1 = gauge(0x100B, 0.1, signed=False, unit="V")
    ovp_l1_time = integer(0x100C, signed=False, unit="ms")
    ovp10 = gauge(0x100D, 0.1, signed=False, unit="V")
    ovp10_time = integer(0x100E, signed=False, unit="s")
    uvp_l1 = gauge(0x100F, 0.1, signed=False, unit="V")
    uvp_l1_time = integer(0x1010, signed=False, unit="ms")
    uvp_l2 = gauge(0x1011, 0.1, signed=False, unit="V")
    uvp_l2_time = integer(0x1012, signed=False, unit="ms")
    ofp_l1 = gauge(0x1013, 0.01, signed=False, unit="Hz")
    ofp_l1_time = integer(0x1014, signed=False, unit="ms")
    ofp_l2 = gauge(0x1015, 0.01, signed=False, unit="Hz")
    ofp_l2_time = integer(0x1016, signed=False, unit="ms")
    ufp_l1 = gauge(0x1017, 0.01, signed=False, unit="Hz")
    ufp_l1_time = integer(0x1018, signed=False, unit="ms")
    ufp_l2 = gauge(0x1019, 0.01, signed=False, unit="Hz")
    ufp_l2_time = integer(0x101A, signed=False, unit="ms")
    ovp_l2 = gauge(0x101B, 0.1, signed=False, unit="V")
    ovp_l2_time = integer(0x101C, signed=False, unit="ms")
    ovp_l3 = gauge(0x101D, 0.1, signed=False, unit="V")
    ovp_l3_time = integer(0x101E, signed=False, unit="ms")
    uvp_l3 = gauge(0x101F, 0.1, signed=False, unit="V")
    uvp_l3_time = integer(0x1020, signed=False, unit="ms")
    ofp_l3 = gauge(0x1021, 0.01, signed=False, unit="Hz")
    ofp_l3_time = integer(0x1022, signed=False, unit="ms")
    ufp_l3 = gauge(0x1023, 0.01, signed=False, unit="Hz")
    ufp_l3_time = integer(0x1024, signed=False, unit="ms")

    field_variants = {
        "grid_meter_ct_enable": Variant.GEN,
        "grid_meter_ct_rate": Variant.GEN,
        "total_energy_feed_to_grid": Variant.GEN,
        "total_energy_consume_from_grid": Variant.GEN,
        "voltage": Variant.GEN | Variant.X1,
        "voltage_l1": Variant.GEN | Variant.X3,
        "voltage_l2": Variant.GEN | Variant.X3,
        "voltage_l3": Variant.GEN | Variant.X3,
        "current": Variant.GEN | Variant.X1,
        "current_l1": Variant.GEN | Variant.X3,
        "current_l2": Variant.GEN | Variant.X3,
        "current_l3": Variant.GEN | Variant.X3,
        "frequency": Variant.GEN,
        "power_l1": Variant.GEN | Variant.X3,
        "power_l2": Variant.GEN | Variant.X3,
        "power_l3": Variant.GEN | Variant.X3,
        "active_power_energy": Variant.GEN,
        "reactive_power": Variant.MAX | Variant.GEN2,
        "total_energy_feed_to_grid_pv": Variant.GEN,
        "active_power_pv_meter": Variant.GEN,
        "grid_regulation": Variant.GEN,
        "ovp_l1": Variant.GEN,
        "ovp_l1_time": Variant.GEN,
        "ovp10": Variant.GEN,
        "ovp10_time": Variant.GEN,
        "uvp_l1": Variant.GEN,
        "uvp_l1_time": Variant.GEN,
        "uvp_l2": Variant.GEN,
        "uvp_l2_time": Variant.GEN,
        "ofp_l1": Variant.GEN,
        "ofp_l1_time": Variant.GEN,
        "ofp_l2": Variant.GEN,
        "ofp_l2_time": Variant.GEN,
        "ufp_l1": Variant.GEN,
        "ufp_l1_time": Variant.GEN,
        "ufp_l2": Variant.GEN,
        "ufp_l2_time": Variant.GEN,
        "ovp_l2": Variant.GEN | Variant.X3,
        "ovp_l2_time": Variant.GEN | Variant.X3,
        "ovp_l3": Variant.GEN | Variant.X3,
        "ovp_l3_time": Variant.GEN | Variant.X3,
        "uvp_l3": Variant.GEN | Variant.X3,
        "uvp_l3_time": Variant.GEN | Variant.X3,
        "ofp_l3": Variant.GEN | Variant.X3,
        "ofp_l3_time": Variant.GEN | Variant.X3,
        "ufp_l3": Variant.GEN | Variant.X3,
        "ufp_l3_time": Variant.GEN | Variant.X3,
    }
