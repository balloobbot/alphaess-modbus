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
