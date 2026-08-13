"""Enumerated register values."""

from __future__ import annotations

from enum import IntEnum


class RunMode(IntEnum):
    """Inverter run mode (0x440)."""

    WAITING = 0
    ONLINE = 1
    UPS_MODE = 2
    BYPASS_MODE = 3
    FAULT_MODE = 4
    DC_MODE = 5
    SELF_TEST_MODE = 6
    CHECK_MODE = 7
    UPDATE_MASTER = 8
    UPDATE_SLAVE = 9
    UPDATE_ARM = 10


class SystemMode(IntEnum):
    """System mode (0x805)."""

    AC = 0
    DC = 1
    HYBRID = 2


class TimePeriodControl(IntEnum):
    """Which of the charge/discharge time periods are active (0x84F)."""

    DISABLED = 0
    CHARGE_ENABLED = 1
    DISCHARGE_ENABLED = 2
    BOTH_ENABLED = 3


class DispatchMode(IntEnum):
    """Control algorithm used when a dispatch command is active (0x885)."""

    PV_ONLY_CHARGE = 1
    SOC_CONTROL = 2
    LOAD_FOLLOWING = 3
    MAXIMISE_OUTPUT = 4
    NORMAL_MODE = 5
    OPTIMISE_CONSUMPTION = 6
    MAXIMISE_CONSUMPTION = 7
    NO_BATTERY_CHARGE = 19


class ResetMode(IntEnum):
    """Inverter reset and restart command codes (0x1100)."""

    ENERGY_TOTALS_RESET = 1
    FACTORY_RESET = 2
    CLEAR_FAULT = 3
    CLEAR_WARNING = 4
    RESTART_DSP = 5
    RESTART_ARM = 6
    RESTART_PCS = 7
    RESTART_EMS = 8


class IpMethod(IntEnum):
    """IP address assignment method (0x0808)."""

    DHCP = 0
    STATIC = 1
