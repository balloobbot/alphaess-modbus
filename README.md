# alphaess-modbus

A standalone Python library that reads and controls an **AlphaESS** storage
inverter over Modbus, exposed as a normal, object-oriented Python API.

The register map (addresses, scales, data types, option lists and the
`allowedtypes` variant masks) is based on the AlphaESS plugin of
[homeassistant-solax-modbus](https://github.com/wills106/homeassistant-solax-modbus)
(Apache-2.0), and is verified in tests against an in-memory mock of the device.

## Design

- It takes a [`modbus_connection.ModbusUnit`](https://github.com/home-assistant-libs/modbus-connection),
  never a connection or a host: you own the link and choose the backend.
- **ASCII framing over TCP is not supported.** Build the connection with an RTU
  or socket framer; this library neither accepts nor forwards `framer="ascii"`.
- A device is a set of sub-systems, each a `Component` with its own registers,
  refreshable on its own and pooled into one set of block reads by
  `async_update()`. Reads are capped at 100 registers per block, the block size
  upstream uses for this device.

| Attribute | What |
| --- | --- |
| `info` | serial number and the master/slave software versions (read once) |
| `grid` | grid voltage, current, frequency, active and reactive power |
| `battery` | voltage, current, SOC, capacity, lifetime charge/discharge energy |
| `inverter` | AC output per phase, frequency, temperature, run mode |
| `eps` | the backup (EPS) output |
| `pv` | up to three MPPT strings |
| `settings` | writable: system mode, unbalance mode, and the charge/discharge schedule |

Field names drop the sub-system prefix from the upstream entity key, so
`grid_voltage_l1` is `device.grid.voltage_l1` and `battery_soc` is
`device.battery.soc`. Home Assistant metadata (icons, device classes, entity
categories) is dropped; units live on the fields.

## Variants

Which registers a device has depends on its variant — the `allowedtypes` bitmask
upstream carries on every entity, modelled here as `Variant` flags (generation
`GEN`/`GEN2`…, phase count `X1`/`X3`, inverter type `HYBRID`/`MAX`…, `EPS`,
`DCB`, `PM`, and the MPPT count). A field is kept when its mask matches the
device's variant — OR within a flag group, AND across groups — and the fields
that don't match are removed from the layout, so their registers are never read.

Upstream derives the variant from the serial number, and only recognises two
prefixes, both of them placeholders for an otherwise unidentified AlphaESS:

| Serial prefix | Variant | Fields |
| --- | --- | --- |
| `XYZ` | `GEN` | 40 of 77 |
| `ZYX` | `MAX \| GEN2 \| MPPT5` | 2 of 77 |

Neither states a phase count, so neither reads the per-phase registers, and the
`ZYX` combination matches almost nothing (its only fields are the serial number
and reactive power) — that is what the upstream masks say. **Pass a variant
explicitly** for a real inverter, e.g. `Variant.GEN | Variant.X3 | Variant.EPS`
for a three-phase hybrid with a backup output.

## Use

```python
import asyncio

from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

from alphaess_modbus import AlphaESS, Variant


async def main() -> None:
    connection = ModbusConnection(ModbusTcpParams(host="192.168.1.50", port=502))
    try:
        unit = connection.for_unit(85)
        device = AlphaESS(unit, Variant.GEN | Variant.X3 | Variant.EPS)
        await device.async_update()

        print("Serial:", device.info.serial_number)
        print("Run mode:", device.inverter.run_mode)
        print("Battery SOC:", device.battery.soc, "%")
        print("PV 1:", device.pv.power_1, "W")
        print("Grid frequency:", device.grid.frequency, "Hz")

        await device.settings.write("charge_target_soc", 90)
    finally:
        await connection.close()


asyncio.run(main())
```

`AlphaESS.async_detect(unit)` builds the device with the variant read from the
serial number instead, raising `UnknownInverterError` when the prefix is not one
of the two above.

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy
```

## License

Apache-2.0, inherited from homeassistant-solax-modbus.
