"""The device object: one AlphaESS inverter over a ``ModbusUnit``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection import ModbusConnectionError, ModbusError, ModbusTimeoutError
from modbus_connection.decode import decode_string
from modbus_connection.model import ComponentGroup

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

# Every component a poll may refresh, in read order, split by what its registers
# hold: what the inverter measures, and what it has been configured to do.
# ``info`` is read separately, only until it succeeds. Each reads for itself, so
# the EPS block (0x40E-0x41B) is now read twice per poll: it sits inside the
# inverter's 0x400-0x41C span, which the inverter reads across. 14 duplicated
# registers buys each block a failure of its own.
_READINGS = ("grid", "battery", "inverter", "eps", "pv")
_SETTINGS = ("settings",)


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

    What the inverter measures and what it has been configured to do refresh
    separately — :meth:`async_update_readings` and :meth:`async_update_settings`
    — so a caller can poll the schedule rarely, or on demand after writing to
    it. :meth:`async_update` does both.
    """

    def __init__(self, unit: ModbusUnit, variant: Variant) -> None:
        self._unit = unit
        self.variant = variant
        self.info = Info(unit, variant)
        self.grid = Grid(unit, variant)
        self.battery = Battery(unit, variant)
        self.inverter = Inverter(unit, variant)
        self.eps = EPS(unit, variant)
        self.pv = PV(unit, variant)
        self.settings = Settings(unit, variant)

        self._readings = [name for name in _READINGS if getattr(self, name).has_fields]
        self._settings = [name for name in _SETTINGS if getattr(self, name).has_fields]
        self._info_read = False

    @classmethod
    async def async_detect(cls, unit: ModbusUnit) -> AlphaESS:
        """Build a device for the inverter on ``unit``, reading its variant."""
        return cls(unit, await async_detect_variant(unit))

    async def async_update_readings(self) -> UpdateReport:
        """Refresh what the inverter measures: grid, battery, inverter, EPS, PV.

        Identity rides along until it is read: it is polled after the rest, and
        dropped from the poll once it succeeds. Last, because it is the one
        block whose failure the poll can shrug off — leading with it would let
        a slow identity read write off a device that is answering.
        """
        names = self._readings if self._info_read else [*self._readings, "info"]
        report = await self._async_poll(names, UpdateReport(set(), {}))
        self._info_read = self._info_read or "info" in report.updated
        return report

    async def async_update_settings(self) -> UpdateReport:
        """Refresh what is configured: system mode and the charge/discharge schedule.

        These change when something writes them, not on their own, so a caller
        that polls them at all polls them rarely — and reads them straight after
        writing one.
        """
        return await self._async_poll(self._settings, UpdateReport(set(), {}))

    async def async_update(self) -> UpdateReport:
        """Refresh readings and settings together, in one report.

        For a caller that does not want to schedule the two apart.
        """
        report = await self.async_update_readings()
        return await self._async_poll(self._settings, report)

    async def _async_poll(self, names: list[str], report: UpdateReport) -> UpdateReport:
        """Read each named component on its own, adding what happened to ``report``.

        Components are read independently, the way upstream reads its blocks: a
        sub-system whose read fails keeps its previous values while the rest
        still refresh. Listeners fire only after every component has been tried,
        and only on the ones that refreshed. A failure of the link itself raises
        ``ModbusConnectionError`` instead of reporting, and so does a timeout
        with nothing answered yet: the device is silent, and walking the rest
        would only pay a full timeout each to learn the same.
        """
        for name in names:
            component: AlphaESSComponent = getattr(self, name)
            try:
                await component.async_update(notify=False)
            except ModbusConnectionError:
                raise
            except ModbusTimeoutError as err:
                if not report.updated and not report.failed:
                    raise  # nothing answered: assume the rest time out too
                report.failed[name] = err
            except ModbusError as err:
                report.failed[name] = err
            else:
                report.updated.add(name)
        for name in names:
            if name in report.updated:
                fresh: AlphaESSComponent = getattr(self, name)
                fresh.notify()
        return report

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Every register this device reads, undecoded — for diagnostics.

        Covers the identity block, which the poll drops once it has read it and
        which is exactly what an issue report needs. Left out are the
        components this variant has no fields for, whose registers a poll never
        asks for either. The reads are pooled, so this is not the poll's shape.

        The fields refresh, but no listener fires: a download is not a poll.
        """
        components = [
            getattr(self, name)
            for name in ("info", *_READINGS, *_SETTINGS)
            if getattr(self, name).has_fields
        ]
        group = ComponentGroup(self._unit, components)
        return await group.async_read_raw(notify=False)
