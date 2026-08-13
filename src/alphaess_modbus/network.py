"""Network settings and IP configuration registers (0x0808 - 0x0810)."""

from __future__ import annotations

from modbus_connection.model import enum, integer
from modbus_connection.model.sunspec import ipaddr

from .component import AlphaESSComponent
from .enums import IpMethod
from .variants import Variant


class Network(AlphaESSComponent):
    """Network settings and IP configuration."""

    ip_method = enum(0x0808, IpMethod)
    local_ip = ipaddr(0x0809)
    subnet_mask = ipaddr(0x080B)
    gateway = ipaddr(0x080D)
    modbus_baud_rate = integer(0x0810, signed=False)

    field_variants = {
        "ip_method": Variant.GEN,
        "local_ip": Variant.GEN,
        "subnet_mask": Variant.GEN,
        "gateway": Variant.GEN,
        "modbus_baud_rate": Variant.GEN,
    }
