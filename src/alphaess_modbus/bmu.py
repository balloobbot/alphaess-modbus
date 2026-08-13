"""Battery Management Unit (BMU) sub-system (0xA000 - 0xB528)."""

from __future__ import annotations

from typing import Any

from modbus_connection.model import gauge, integer, uint32

from .component import AlphaESSComponent
from .variants import ANY, Variant, matches


class BMUModule(AlphaESSComponent):
    """Telemetry for a single battery module (0xA200 base, stride 0x100)."""

    sn = uint32(0xA200, nan=(0x0000_0000,0xFFFF_FFFF))
    soft_version = gauge(0xA202, 0.01)
    hard_version = gauge(0xA203, 0.01)
    state = integer(0xA204, signed=False)
    cluster_voltage = gauge(0xA205, 0.1, signed=False, unit="V")
    cluster_current = gauge(0xA206, 0.1, signed=True, unit="A")
    insulated_resistance = integer(0xA207, signed=False, unit="kΩ")
    soc = integer(0xA208, signed=False, unit="%")
    soh = integer(0xA209, signed=False, unit="%")
    lmu_communication = uint32(0xA20A)
    temperature_sensor_failure = uint32(0xA20C)
    wireharness_failure = uint32(0xA20E)
    equalization = uint32(0xA210)
    equalization_mos_failure = uint32(0xA212)
    iso_soft_version = gauge(0xA214, 0.01)
    iso_hard_version = gauge(0xA215, 0.01)
    passive_equalization = uint32(0xA216)
    boost_equalization = uint32(0xA218)
    buck_equalization = uint32(0xA21A)
    lmu_number = integer(0xA21C, signed=False)
    single_cut_fault_code = integer(0xA21D, signed=False)
    reset_log = integer(0xA21E, signed=False)
    restarts_number = integer(0xA21F, signed=False)
    version = integer(0xA220, signed=False)
    min_cell_voltage = gauge(0xA221, 0.001, signed=False, unit="V")
    min_cell_voltage_id = integer(0xA222, signed=False)
    max_cell_voltage = gauge(0xA223, 0.001, signed=False, unit="V")
    max_cell_voltage_id = integer(0xA224, signed=False)
    min_cell_temperature = integer(0xA225, signed=True, unit="°C")
    min_cell_temperature_id = integer(0xA226, signed=False)
    max_cell_temperature = integer(0xA227, signed=True, unit="°C")
    max_cell_temperature_id = integer(0xA228, signed=False)

    field_variants = {
        "sn": ANY,
        "soft_version": ANY,
        "hard_version": ANY,
        "state": ANY,
        "cluster_voltage": ANY,
        "cluster_current": ANY,
        "insulated_resistance": ANY,
        "soc": ANY,
        "soh": ANY,
        "lmu_communication": ANY,
        "temperature_sensor_failure": ANY,
        "wireharness_failure": ANY,
        "equalization": ANY,
        "equalization_mos_failure": ANY,
        "iso_soft_version": ANY,
        "iso_hard_version": ANY,
        "passive_equalization": ANY,
        "boost_equalization": ANY,
        "buck_equalization": ANY,
        "lmu_number": ANY,
        "single_cut_fault_code": ANY,
        "reset_log": ANY,
        "restarts_number": ANY,
        "version": ANY,
        "min_cell_voltage": ANY,
        "min_cell_voltage_id": ANY,
        "max_cell_voltage": ANY,
        "max_cell_voltage_id": ANY,
        "min_cell_temperature": ANY,
        "min_cell_temperature_id": ANY,
        "max_cell_temperature": ANY,
        "max_cell_temperature_id": ANY,
    }


class BMU(AlphaESSComponent):
    """Top-level BMU summary and repeated battery modules (0xA000 base)."""

    sn = uint32(0xA000)
    soft_version = gauge(0xA002, 0.01)
    protocol_version = integer(0xA003, signed=False)
    hard_version = gauge(0xA004, 0.01)
    max_charge_current = gauge(0xA005, 0.1, signed=False, unit="A")
    max_discharge_current = gauge(0xA006, 0.1, signed=False, unit="A")
    status_flag = integer(0xA007, signed=False)
    max_pole_temperature = gauge(0xA008, 0.1, signed=True, unit="°C")
    voltage = gauge(0xA009, 0.1, signed=False, unit="V")
    current = gauge(0xA00A, 0.1, signed=True, unit="A")
    insulated_resistance = integer(0xA00B, signed=False, unit="kΩ")
    soc = integer(0xA00C, signed=False, unit="%")
    soh = integer(0xA00D, signed=False, unit="%")
    min_cell_voltage = gauge(0xA00E, 0.001, signed=False, unit="V")
    min_cell_voltage_id = integer(0xA00F, signed=False)
    max_cell_voltage = gauge(0xA010, 0.001, signed=False, unit="V")
    max_cell_voltage_id = integer(0xA011, signed=False)
    min_cell_temperature = gauge(0xA012, 0.1, signed=True, unit="°C")
    min_cell_temperature_id = integer(0xA013, signed=False)
    max_cell_temperature = gauge(0xA014, 0.1, signed=True, unit="°C")
    max_cell_temperature_id = integer(0xA015, signed=False)
    max_pole_temperature_id = integer(0xA016, signed=False)
    restarts_number = integer(0xA01C, signed=False)
    clusters_number = integer(0xA01D, signed=False)

    field_variants = {
        "sn": Variant.GEN,
        "soft_version": Variant.GEN,
        "protocol_version": Variant.GEN,
        "hard_version": Variant.GEN,
        "max_charge_current": Variant.GEN,
        "max_discharge_current": Variant.GEN,
        "status_flag": Variant.GEN,
        "max_pole_temperature": Variant.GEN,
        "voltage": Variant.GEN,
        "current": Variant.GEN,
        "insulated_resistance": Variant.GEN,
        "soc": Variant.GEN,
        "soh": Variant.GEN,
        "min_cell_voltage": Variant.GEN,
        "min_cell_voltage_id": Variant.GEN,
        "max_cell_voltage": Variant.GEN,
        "max_cell_voltage_id": Variant.GEN,
        "min_cell_temperature": Variant.GEN,
        "min_cell_temperature_id": Variant.GEN,
        "max_cell_temperature": Variant.GEN,
        "max_cell_temperature_id": Variant.GEN,
        "max_pole_temperature_id": Variant.GEN,
        "restarts_number": Variant.GEN,
        "clusters_number": Variant.GEN,
    }

    @property
    def has_fields(self) -> bool:
        """BMU is present on GEN variant inverters."""
        return matches(self.variant, Variant.GEN)

    @property
    def resolved_fields(self) -> dict[str, Any]:
        if not self.has_fields:
            return {}
        return dict(super().resolved_fields)
