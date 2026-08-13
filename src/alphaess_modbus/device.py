"""The device object: one AlphaESS inverter over a ``ModbusUnit``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection import ModbusConnectionError, ModbusError
from modbus_connection.decode import decode_string

from .battery import Battery
from .component import AlphaESSComponent, UpdateReport
from .eps import EPS
from .grid import Grid
from .info import SERIAL_NUMBER_ADDRESS, SERIAL_NUMBER_LENGTH, Info
from .inverter import Inverter
from .pv import PV
from .settings import Settings
from .variants import UnknownInverterError, Variant, variant_from_serial

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

# Every component a poll may refresh, in read order; ``info`` is read separately,
# only until it succeeds. Each reads for itself, so the EPS block (0x40E-0x41B)
# is now read twice per poll: it sits inside the inverter's 0x400-0x41C span,
# which the inverter reads across. 14 duplicated registers buys each block a
# failure of its own.
_POLLED = ("grid", "battery", "inverter", "eps", "pv", "settings")


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

        self._polled = [name for name in _POLLED if getattr(self, name).has_fields]
        self._info_read = False

    @classmethod
    async def async_detect(cls, unit: ModbusUnit) -> AlphaESS:
        """Build a device for the inverter on ``unit``, reading its variant."""
        return cls(unit, await async_detect_variant(unit))

    async def async_update(self) -> UpdateReport:
        """Refresh every polled sub-system, one at a time.

        Components are read independently, the way upstream reads its blocks: a
        sub-system whose read fails keeps its previous values while the rest
        still refresh. Listeners fire only after every component has been tried,
        and only on the ones that refreshed. A failure of the link itself raises
        ``ModbusConnectionError`` instead of reporting.

        Identity rides along until it is read: it is polled with the rest, and
        dropped from the poll once it succeeds.
        """
        updated: set[str] = set()
        failed: dict[str, ModbusError] = {}
        names = self._polled if self._info_read else ["info", *self._polled]
        for name in names:
            component: AlphaESSComponent = getattr(self, name)
            try:
                await component.async_update(notify=False)
            except ModbusConnectionError:
                raise
            except ModbusError as err:
                failed[name] = err
            else:
                updated.add(name)
        self._info_read = self._info_read or "info" in updated
        for name in updated:
            fresh: AlphaESSComponent = getattr(self, name)
            fresh.notify()
        return UpdateReport(updated, failed)
