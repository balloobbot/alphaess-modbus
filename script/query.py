#!/usr/bin/env python3

"""Query an AlphaESS storage inverter and print every value.

Reads one inverter once and dumps it to the terminal — the quickest way to
check a real device with no application around it.

::

    uv run script/query.py 192.168.1.50 --unit 85 --variant GEN,X3,EPS
    uv run script/query.py /dev/ttyUSB0 --transport serial --unit 85
"""

from __future__ import annotations

import argparse
import asyncio

from modbus_connection import ModbusError
from modbus_connection.cli_helper import (
    CountingUnit,
    add_connection_args,
    connect_from_args,
    print_component,
)

from alphaess_modbus import AlphaESS, UnknownInverterError, Variant

# The inverter is RS-485 RTU; over TCP it is reached through a gateway, which
# presents it either transparently (rtu) or as native Modbus TCP (socket).
CONNECTIONS = (("serial", "rtu"), ("tcp", "rtu"), ("tcp", "socket"))

# Identity first, then the sub-systems in poll order. ``info`` rides in the poll
# only until it succeeds, so it is not in the polled set but does hold values
# after an update.
COMPONENTS = ("info", "grid", "battery", "inverter", "eps", "pv", "settings")


def parse_variant(text: str) -> Variant:
    """Turn ``GEN,X3,EPS`` into the variant flags it names."""
    variant = Variant(0)
    for part in text.split(","):
        name = part.strip().upper()
        try:
            variant |= Variant[name]
        except KeyError:
            raise argparse.ArgumentTypeError(f"unknown variant flag {name!r}") from None
    return variant


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_connection_args(parser, connections=CONNECTIONS)
    parser.add_argument("--unit", type=int, default=85, help="Modbus unit id")
    parser.add_argument(
        "--variant",
        type=parse_variant,
        help="variant flags, e.g. GEN,X3,EPS; read from the serial number if omitted",
    )
    args = parser.parse_args()

    try:
        connection = await connect_from_args(args)
    except ModbusError as err:
        print(f"Could not connect: {err}")
        return 1

    counting = CountingUnit(connection.for_unit(args.unit))
    try:
        if args.variant is None:
            device = await AlphaESS.async_detect(counting)
        else:
            device = AlphaESS(counting, args.variant)
        await device.async_update()
    except UnknownInverterError as err:
        print(f"{err}; pass --variant to read it anyway")
        return 1
    except ModbusError as err:
        print(f"Could not read the inverter: {err}")
        return 1
    finally:
        await connection.close()

    print(f"Variant: {device.variant.name}")
    for name in COMPONENTS:
        component = getattr(device, name)
        if not component.has_fields:  # this variant has none of its registers
            continue
        print()
        print_component(component, title=name)
    print(f"\n{counting.reads} Modbus reads")
    return 0


raise SystemExit(asyncio.run(main()))
