"""Inverter variant flags and the rule that decides which fields a variant has.

Ported from the ``allowedtypes`` bitmask of ``plugin_alphaess.py`` in
homeassistant-solax-modbus. A field carries a mask; a device carries a variant.
The flags are split into groups (generation, phases, inverter type, EPS, DCB,
PM, MPPT count). Within a group the bits a mask names are OR-ed, across groups
the results are AND-ed, and a group a mask says nothing about always matches.
"""

from __future__ import annotations

from enum import IntFlag


class Variant(IntFlag):
    """What an AlphaESS inverter is, and which optional parts to read."""

    GEN = 0x0001
    GEN2 = 0x0002
    GEN3 = 0x0004
    GEN4 = 0x0008
    GEN5 = 0x0010

    X1 = 0x0100  # single phase
    X3 = 0x0200  # three phase

    PV = 0x0400
    AC = 0x0800
    HYBRID = 0x1000
    MIC = 0x2000
    MAX = 0x4000

    EPS = 0x8000  # emergency power supply, read on request
    DCB = 0x10000  # dry contact box, read on request
    PM = 0x20000  # power meter, read on request

    MPPT3 = 0x40000
    MPPT4 = 0x80000
    MPPT5 = 0x100000
    MPPT6 = 0x200000
    MPPT10 = 0x400000


ANY = Variant(0)
"""Mask of a field every variant has."""

_GROUPS: tuple[Variant, ...] = (
    Variant.GEN | Variant.GEN2 | Variant.GEN3 | Variant.GEN4 | Variant.GEN5,
    Variant.X1 | Variant.X3,
    Variant.PV | Variant.AC | Variant.HYBRID | Variant.MIC | Variant.MAX,
    Variant.EPS,
    Variant.DCB,
    Variant.PM,
    Variant.MPPT3 | Variant.MPPT4 | Variant.MPPT5 | Variant.MPPT6 | Variant.MPPT10,
)


def matches(variant: Variant, mask: Variant) -> bool:
    """Return whether a device of ``variant`` has a field declared with ``mask``."""
    return all(not (mask & group) or bool(variant & mask & group) for group in _GROUPS)


def variant_from_serial(serial: str) -> Variant | None:
    """Derive the variant from a serial number, or ``None`` if unrecognized.

    The two prefixes are the ones upstream ships; both are placeholders for an
    otherwise unidentified AlphaESS, and neither says whether the inverter is
    single- or three-phase. Pass a variant explicitly to read the X1/X3 fields.
    """
    if serial.startswith("XYZ"):
        return Variant.GEN
    if serial.startswith("ZYX"):
        return Variant.MAX | Variant.GEN2 | Variant.MPPT5
    return None


class UnknownInverterError(Exception):
    """The serial number does not identify a known AlphaESS variant."""
