"""Identity registers (0x640 - 0x653), read once at setup."""

from __future__ import annotations

from modbus_connection.model import string

from .component import AlphaESSComponent
from .fields import version_triple
from .variants import ANY, Variant

SERIAL_NUMBER_ADDRESS = 0x64A
SERIAL_NUMBER_LENGTH = 10


class Info(AlphaESSComponent):
    """Serial number and firmware versions."""

    software_master_version = string(0x640, 5)
    # Upstream reads 8 registers here, which runs into the serial number below.
    software_slave_version = string(0x645, 8)
    serial_number = string(SERIAL_NUMBER_ADDRESS, SERIAL_NUMBER_LENGTH)
    ems_serial_number = string(0x0743, 8)
    ems_version = version_triple(0x074B)

    field_variants = {
        "software_master_version": Variant.GEN,
        "software_slave_version": Variant.GEN,
        "serial_number": ANY,
        "ems_serial_number": Variant.GEN,
        "ems_version": Variant.GEN,
    }
