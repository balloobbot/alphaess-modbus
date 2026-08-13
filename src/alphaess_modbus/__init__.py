"""alphaess-modbus — read and control an AlphaESS storage inverter over Modbus.

Construct ``AlphaESS(unit, variant)`` with a ``modbus_connection.ModbusUnit``,
call ``await device.async_update()``, then read its sub-systems as normal Python
objects::

    device.grid.frequency
    device.battery.soc
    device.inverter.run_mode
    device.pv.power_1
    await device.settings.write("charge_target_soc", 90)

Which registers a device has depends on its variant (generation, phase count,
MPPT count, EPS); see ``variants.Variant``. ASCII framing over TCP is not
supported: build the connection with an RTU or socket framer.

The register map is derived from the AlphaESS plugin of
`homeassistant-solax-modbus <https://github.com/wills106/homeassistant-solax-modbus>`_.
"""

from .battery import Battery
from .component import AlphaESSComponent, UpdateReport
from .device import AlphaESS, async_detect_variant
from .enums import RunMode, SystemMode, TimePeriodControl
from .eps import EPS
from .grid import Grid
from .info import Info
from .inverter import Inverter
from .pv import PV
from .settings import Settings
from .variants import ANY, UnknownInverterError, Variant, matches, variant_from_serial

__all__ = [
    "ANY",
    "EPS",
    "PV",
    "AlphaESS",
    "AlphaESSComponent",
    "Battery",
    "Grid",
    "Info",
    "Inverter",
    "RunMode",
    "Settings",
    "SystemMode",
    "TimePeriodControl",
    "UnknownInverterError",
    "UpdateReport",
    "Variant",
    "async_detect_variant",
    "matches",
    "variant_from_serial",
]
