"""Writable settings: system mode and the charge/discharge time periods."""

from __future__ import annotations

from modbus_connection.model import boolean, enum, integer

from .component import AlphaESSComponent, in_range
from .enums import SystemMode, TimePeriodControl
from .variants import Variant

_HOUR = in_range(0, 23)
_MINUTE = in_range(0, 59)
_SOC = in_range(10, 99)


class Settings(AlphaESSComponent):
    """Everything the inverter accepts a write on (0x805 - 0x861)."""

    system_mode = enum(0x805, SystemMode, writable=True)
    three_phase_unbalance_mode = boolean(0x811, writable=True)
    # Upstream spells this key "time_preiod_control".
    time_period_control = enum(0x84F, TimePeriodControl, writable=True)
    discharge_minimum_soc = integer(0x850, signed=False, writable=_SOC, unit="%")
    discharge_start_1_hours = integer(0x851, signed=False, writable=_HOUR, unit="h")
    discharge_stop_1_hours = integer(0x852, signed=False, writable=_HOUR, unit="h")
    discharge_start_2_hours = integer(0x853, signed=False, writable=_HOUR, unit="h")
    discharge_stop_2_hours = integer(0x854, signed=False, writable=_HOUR, unit="h")
    charge_target_soc = integer(0x855, signed=False, writable=_SOC, unit="%")
    charge_start_1_hours = integer(0x856, signed=False, writable=_HOUR, unit="h")
    charge_stop_1_hours = integer(0x857, signed=False, writable=_HOUR, unit="h")
    charge_start_2_hours = integer(0x858, signed=False, writable=_HOUR, unit="h")
    charge_stop_2_hours = integer(0x859, signed=False, writable=_HOUR, unit="h")
    discharge_start_1_mins = integer(0x85A, signed=False, writable=_MINUTE, unit="min")
    discharge_stop_1_mins = integer(0x85B, signed=False, writable=_MINUTE, unit="min")
    discharge_start_2_mins = integer(0x85C, signed=False, writable=_MINUTE, unit="min")
    discharge_stop_2_mins = integer(0x85D, signed=False, writable=_MINUTE, unit="min")
    charge_start_1_mins = integer(0x85E, signed=False, writable=_MINUTE, unit="min")
    charge_stop_1_mins = integer(0x85F, signed=False, writable=_MINUTE, unit="min")
    charge_start_2_mins = integer(0x860, signed=False, writable=_MINUTE, unit="min")
    charge_stop_2_mins = integer(0x861, signed=False, writable=_MINUTE, unit="min")

    field_variants = {
        "system_mode": Variant.GEN,
        "three_phase_unbalance_mode": Variant.GEN | Variant.X3,
        "time_period_control": Variant.GEN,
        "discharge_minimum_soc": Variant.GEN,
        "discharge_start_1_hours": Variant.GEN,
        "discharge_stop_1_hours": Variant.GEN,
        "discharge_start_2_hours": Variant.GEN,
        "discharge_stop_2_hours": Variant.GEN,
        "charge_target_soc": Variant.GEN,
        "charge_start_1_hours": Variant.GEN,
        "charge_stop_1_hours": Variant.GEN,
        "charge_start_2_hours": Variant.GEN,
        "charge_stop_2_hours": Variant.GEN,
        "discharge_start_1_mins": Variant.GEN,
        "discharge_stop_1_mins": Variant.GEN,
        "discharge_start_2_mins": Variant.GEN,
        "discharge_stop_2_mins": Variant.GEN,
        "charge_start_1_mins": Variant.GEN,
        "charge_stop_1_mins": Variant.GEN,
        "charge_start_2_mins": Variant.GEN,
        "charge_stop_2_mins": Variant.GEN,
    }
