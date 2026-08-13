"""Base component: every AlphaESS sub-system filters its fields by variant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from modbus_connection import ModbusError
from modbus_connection.model import Component, WriteValidator

from .variants import Variant, matches

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


class AlphaESSComponent(Component):
    """A sub-system, narrowed to the fields the device's variant has.

    ``field_variants`` maps every declared field to its ``allowedtypes`` mask;
    the fields that do not match are dropped from the layout, so their registers
    are never read.
    """

    # Upstream reads this device in blocks of at most 100 registers.
    max_span = 100

    field_variants: ClassVar[dict[str, Variant]] = {}

    def __init__(self, unit: ModbusUnit, variant: Variant) -> None:
        super().__init__(unit)
        self.variant = variant
        self.restrict_fields(
            [
                name
                for name, mask in self.field_variants.items()
                if matches(variant, mask)
            ]
        )

    @property
    def has_fields(self) -> bool:
        """Whether this variant has any of this sub-system's fields."""
        return bool(self.resolved_fields)


@dataclass(frozen=True)
class UpdateReport:
    """What one poll refreshed, by the device's component attribute names.

    A failed component kept its previous values and did not notify; the error
    that failed it rides along. A dead link is never in here — the update
    raises ``ModbusConnectionError`` instead of reporting partial silence.
    """

    updated: set[str]
    failed: dict[str, ModbusError]

    @property
    def complete(self) -> bool:
        """Whether every polled component refreshed."""
        return not self.failed


def in_range(low: int, high: int) -> WriteValidator:
    """Reject a write outside the range the inverter accepts."""

    def validate(value: Any) -> int:
        number = int(value)
        if not low <= number <= high:
            raise ValueError(f"{value!r} outside {low}-{high}")
        return number

    return validate
