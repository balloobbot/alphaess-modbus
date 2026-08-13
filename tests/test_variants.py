"""The variant flags, the mask rule and how a variant narrows each sub-system."""

from __future__ import annotations

import itertools

import pytest
from modbus_connection.mock import MockModbusUnit

from alphaess_modbus import (
    BMU,
    EPS,
    PV,
    AlphaESS,
    AlphaESSComponent,
    Battery,
    BMUModule,
    Grid,
    Info,
    Inverter,
    Network,
    Settings,
    UnknownInverterError,
    Variant,
    async_detect_variant,
    matches,
    variant_from_serial,
)

COMPONENTS: tuple[type[AlphaESSComponent], ...] = (
    Info,
    Grid,
    Battery,
    BMU,
    BMUModule,
    Inverter,
    EPS,
    PV,
    Settings,
    Network,
)


# The upstream groups, as literal ints, so a typo in Variant would show up.
_GEN_GROUP = 0x0001 | 0x0002 | 0x0004 | 0x0008 | 0x0010
_X_GROUP = 0x0100 | 0x0200
_TYPE_GROUP = 0x0400 | 0x0800 | 0x1000 | 0x2000 | 0x4000
_EPS_GROUP = 0x8000
_DCB_GROUP = 0x10000
_PM_GROUP = 0x20000
_MPPT_GROUP = 0x40000 | 0x80000 | 0x100000 | 0x200000 | 0x400000


def upstream_match(spec: int, mask: int) -> bool:
    """``plugin_alphaess.matchInverterWithMask``, transcribed."""
    genmatch = ((spec & mask & _GEN_GROUP) != 0) or (mask & _GEN_GROUP == 0)
    xmatch = ((spec & mask & _X_GROUP) != 0) or (mask & _X_GROUP == 0)
    hybmatch = ((spec & mask & _TYPE_GROUP) != 0) or (mask & _TYPE_GROUP == 0)
    epsmatch = ((spec & mask & _EPS_GROUP) != 0) or (mask & _EPS_GROUP == 0)
    dcbmatch = ((spec & mask & _DCB_GROUP) != 0) or (mask & _DCB_GROUP == 0)
    mpptmatch = ((spec & mask & _MPPT_GROUP) != 0) or (mask & _MPPT_GROUP == 0)
    pmmatch = ((spec & mask & _PM_GROUP) != 0) or (mask & _PM_GROUP == 0)
    return (
        genmatch
        and xmatch
        and hybmatch
        and epsmatch
        and dcbmatch
        and mpptmatch
        and pmmatch
    )


def test_matches_agrees_with_upstream() -> None:
    """Every declared mask, against every combination of the flags in play."""
    masks = {
        mask for component in COMPONENTS for mask in component.field_variants.values()
    }
    interesting = (
        Variant.GEN,
        Variant.GEN2,
        Variant.X1,
        Variant.X3,
        Variant.HYBRID,
        Variant.MAX,
        Variant.EPS,
        Variant.MPPT3,
        Variant.MPPT5,
    )
    for count in range(len(interesting) + 1):
        for combination in itertools.combinations(interesting, count):
            spec = Variant(0)
            for flag in combination:
                spec |= flag
            for mask in masks:
                assert matches(spec, mask) == upstream_match(int(spec), int(mask)), (
                    f"{spec!r} vs {mask!r}"
                )


def test_every_declared_field_has_a_mask() -> None:
    for component in COMPONENTS:
        assert set(component.field_variants) == set(component.declared_fields), (
            component.__name__
        )


def test_serial_number_prefixes() -> None:
    assert variant_from_serial("XYZ123") is Variant.GEN
    assert variant_from_serial("ZYX123") == (Variant.MAX | Variant.GEN2 | Variant.MPPT5)
    assert variant_from_serial("AL1234") is None


async def test_detect_reads_the_serial_number(unit: MockModbusUnit) -> None:
    assert await async_detect_variant(unit) is Variant.GEN
    device = await AlphaESS.async_detect(unit)
    assert device.variant is Variant.GEN


async def test_detect_rejects_an_unknown_serial(unit: MockModbusUnit) -> None:
    unit.holding[0x64A] = 0x4142  # "AB..."
    with pytest.raises(UnknownInverterError):
        await async_detect_variant(unit)


@pytest.mark.parametrize(
    ("variant", "expected"),
    [
        # The two variants upstream detects from a serial number.
        (
            Variant.GEN,
            {
                "Info": 5,
                "Grid": 25,
                "Battery": 38,
                "BMU": 24,
                "Inverter": 16,
                "EPS": 0,
                "PV": 14,
                "Settings": 29,
                "Network": 5,
            },
        ),
        (
            Variant.MAX | Variant.GEN2 | Variant.MPPT5,
            {
                "Info": 1,
                "Grid": 1,
                "Battery": 0,
                "BMU": 0,
                "Inverter": 0,
                "EPS": 0,
                "PV": 0,
                "Settings": 0,
                "Network": 0,
            },
        ),
        # Variants a caller can state explicitly.
        (
            Variant.GEN | Variant.X1,
            {
                "Info": 5,
                "Grid": 27,
                "Battery": 38,
                "BMU": 24,
                "Inverter": 18,
                "EPS": 2,
                "PV": 14,
                "Settings": 29,
                "Network": 5,
            },
        ),
        (
            Variant.GEN | Variant.X3 | Variant.EPS | Variant.MPPT3,
            {
                "Info": 5,
                "Grid": 44,
                "Battery": 38,
                "BMU": 24,
                "Inverter": 25,
                "EPS": 10,
                "PV": 23,
                "Settings": 30,
                "Network": 5,
            },
        ),
    ],
)
async def test_field_counts_per_variant(
    unit: MockModbusUnit, variant: Variant, expected: dict[str, int]
) -> None:
    device = AlphaESS(unit, variant)
    await device.async_update()
    components = (
        device.info,
        device.grid,
        device.battery,
        device.bmu,
        device.inverter,
        device.eps,
        device.pv,
        device.settings,
        device.network,
    )
    names = (
        "Info",
        "Grid",
        "Battery",
        "BMU",
        "Inverter",
        "EPS",
        "PV",
        "Settings",
        "Network",
    )
    counts = {
        name: 0 if component is None else len(component.resolved_fields)
        for component, name in zip(components, names, strict=True)
    }
    assert counts == expected


def test_all_fields_are_reachable_by_some_variant(unit: MockModbusUnit) -> None:
    """No field is unreachable."""
    everything = (
        Variant.GEN
        | Variant.X3
        | Variant.EPS
        | Variant.MPPT3
        | Variant.MPPT4
        | Variant.MPPT5
    )
    reachable: set[tuple[str, str]] = set()
    for variant in (
        everything,
        everything | Variant.X1,
        Variant.HYBRID | Variant.GEN2,
        Variant.MAX | Variant.GEN2,
    ):
        for component_class in COMPONENTS:
            component = component_class(unit, variant)
            reachable |= {
                (component_class.__name__, name) for name in component.resolved_fields
            }
    declared = {
        (component_class.__name__, name)
        for component_class in COMPONENTS
        for name in component_class.declared_fields
    }
    assert reachable == declared
    assert len(declared) == 247


def test_a_variant_without_fields_is_not_polled(unit: MockModbusUnit) -> None:
    device = AlphaESS(unit, Variant.GEN)
    assert device.eps.has_fields is False
    assert device.eps not in device.polled_components
