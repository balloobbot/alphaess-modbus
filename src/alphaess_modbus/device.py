"""The device object: one AlphaESS inverter over a ``ModbusUnit``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection import IllegalDataAddressError
from modbus_connection.decode import decode_string
from modbus_connection.model import ComponentGroup

from .battery import Battery
from .bmu import BMU, BMUModule
from .component import AlphaESSComponent
from .eps import EPS
from .grid import Grid
from .info import SERIAL_NUMBER_ADDRESS, SERIAL_NUMBER_LENGTH, Info
from .inverter import Inverter
from .network import Network
from .pv import PV
from .settings import Settings
from .variants import UnknownInverterError, Variant, variant_from_serial

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


async def _optional[C: AlphaESSComponent](component: C) -> C | None:
    """Read an optional sub-system; None if this device does not have it."""
    if not component.has_fields:
        return None

    try:
        await component.async_update()
    except IllegalDataAddressError:
        return None
    return component


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
        self._unit = unit
        self.variant = variant
        self.info = Info(unit, variant)
        self.grid = Grid(unit, variant)
        self.inverter = Inverter(unit, variant)
        self.eps = EPS(unit, variant)
        self.pv = PV(unit, variant)
        self.settings = Settings(unit, variant)
        self.network = Network(unit, variant)

        # Optional components: probed during setup phase
        self.battery: Battery | None = None
        self.bmu: BMU | None = None
        self.bmu_modules: list[BMUModule] = []

        self.polled_components: list[AlphaESSComponent] = []
        self._group: ComponentGroup | None = None


    @classmethod
    async def async_detect(cls, unit: ModbusUnit) -> AlphaESS:
        """Build a device for the inverter on ``unit``, reading its variant."""
        return cls(unit, await async_detect_variant(unit))

    async def _async_setup(self) -> None:
        """Read identity once, probe optional sub-systems, build group."""
        await self.info.async_update()

        # Probe optional battery
        self.battery = await _optional(Battery(self._unit, self.variant))

        # Probe top-level BMU
        self.bmu = await _optional(BMU(self._unit, self.variant))

        # Probe BMU modules by serial number
        self.bmu_modules = []
        if self.bmu is not None:
            for i in range(20):
                probed_module = await _optional(
                    BMUModule(
                        self._unit,
                        self.variant,
                        base_offset=i * 0x100,
                    )
                )
                if probed_module is None or probed_module.sn is None:
                    break
                self.bmu_modules.append(probed_module)

        self.polled_components = [
            component
            for component in (
                self.grid,
                self.battery,
                self.bmu,
                *self.bmu_modules,
                self.inverter,
                self.eps,
                self.pv,
                self.settings,
                self.network,
            )
            if component is not None and component.has_fields
        ]

        self._group = ComponentGroup(self._unit, self.polled_components)

    async def async_update(self) -> None:
        """Refresh every polled sub-system; the first call also reads identity."""
        if self._group is None:
            await self._async_setup()
        assert self._group is not None
        await self._group.async_update()

