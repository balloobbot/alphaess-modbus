"""The device object: one AlphaESS inverter over a ``ModbusUnit``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection.decode import decode_string
from modbus_connection.model import ComponentGroup

from .battery import Battery
from .eps import EPS
from .grid import Grid
from .info import SERIAL_NUMBER_ADDRESS, SERIAL_NUMBER_LENGTH, Info
from .inverter import Inverter
from .pv import PV
from .settings import Settings
from .variants import UnknownInverterError, Variant, variant_from_serial

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


async def async_detect_variant(unit: ModbusUnit) -> Variant:
    """Read the serial number and derive the inverter variant from it."""
    words = await unit.read_holding_registers(
        SERIAL_NUMBER_ADDRESS, SERIAL_NUMBER_LENGTH
    )
    serial = decode_string(words)
    variant = variant_from_serial(serial)
    if variant is None:
        raise UnknownInverterError(f"unrecognized AlphaESS serial number: {serial!r}")
    return variant


class AlphaESS:
    """An AlphaESS storage inverter.

    The variant decides which registers exist on this device; pass it, or use
    :meth:`async_detect` to derive it from the serial number.
    """

    def __init__(self, unit: ModbusUnit, variant: Variant) -> None:
        self.variant = variant
        self.info = Info(unit, variant)
        self.grid = Grid(unit, variant)
        self.battery = Battery(unit, variant)
        self.inverter = Inverter(unit, variant)
        self.eps = EPS(unit, variant)
        self.pv = PV(unit, variant)
        self.settings = Settings(unit, variant)

        self.polled_components = [
            component
            for component in (
                self.grid,
                self.battery,
                self.inverter,
                self.eps,
                self.pv,
                self.settings,
            )
            if component.has_fields
        ]
        self._group = ComponentGroup(unit, self.polled_components)
        self._info_read = False

    @classmethod
    async def async_detect(cls, unit: ModbusUnit) -> AlphaESS:
        """Build a device for the inverter on ``unit``, reading its variant."""
        return cls(unit, await async_detect_variant(unit))

    async def async_update(self) -> None:
        """Refresh every polled sub-system; the first call also reads identity."""
        if not self._info_read:
            await self.info.async_update()
            self._info_read = True
        await self._group.async_update()
