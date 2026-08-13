"""Custom register field primitives for AlphaESS Modbus."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from modbus_connection.model import RegisterField, WriteValidator


def _bcd2dec(val: int) -> int:
    return (val >> 4) * 10 + (val & 0xF)


def _dec2bcd(val: int) -> int:
    return ((val // 10) << 4) | (val % 10)


class RtcField(RegisterField[datetime]):
    """The real-time clock: three registers holding BCD-packed (YYMM, DDHH, MMSS)."""

    def __init__(
        self, address: int, *, writable: bool | WriteValidator = False
    ) -> None:
        super().__init__(address, count=3, writable=writable)

    def decode(
        self, words: list[int], scale_exponent: int | None = None
    ) -> datetime | None:
        if len(words) < 3:
            return None
        yymm, ddhh, mmss = words[:3]
        try:
            year = 2000 + _bcd2dec((yymm >> 8) & 0xFF)
            month = _bcd2dec(yymm & 0xFF)
            day = _bcd2dec((ddhh >> 8) & 0xFF)
            hour = _bcd2dec(ddhh & 0xFF)
            minute = _bcd2dec((mmss >> 8) & 0xFF)
            second = _bcd2dec(mmss & 0xFF)
            return datetime(year, month, day, hour, minute, second)
        except ValueError:
            return None

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        if not isinstance(value, datetime):
            raise ValueError(f"expected datetime, got {value!r}")
        year = value.year % 100
        yymm = (_dec2bcd(year) << 8) | _dec2bcd(value.month)
        ddhh = (_dec2bcd(value.day) << 8) | _dec2bcd(value.hour)
        mmss = (_dec2bcd(value.minute) << 8) | _dec2bcd(value.second)
        return [yymm, ddhh, mmss]


def rtc(address: int, *, writable: bool = False) -> RtcField:
    """Create a real-time-clock datetime field."""
    return RtcField(address, writable=writable)


class VersionTripleField(RegisterField[str]):
    """Version string over three registers formatted as <high>.<middle>.<low>."""

    def __init__(self, address: int) -> None:
        super().__init__(address, count=3, writable=False)

    def decode(self, words: list[int], scale_exponent: int | None = None) -> str | None:
        if len(words) < 3:
            return None
        high, middle, low = words[:3]
        return f"{high}.{middle}.{low}"


def version_triple(address: int) -> VersionTripleField:
    """Create a version string field over 3 registers (<high>.<middle>.<low>)."""
    return VersionTripleField(address)
