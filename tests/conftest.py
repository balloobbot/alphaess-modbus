"""A mock AlphaESS inverter, seeded with raw register values.

The mock backend ships with modbus-connection as an auto-registered pytest
plugin, so there is no server, socket or real backend here.
"""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from alphaess_modbus import AlphaESS, Variant

FULL = Variant.GEN | Variant.X3 | Variant.EPS | Variant.MPPT3
"""A variant that has every field except the two upstream gates on MAX/GEN2."""


def ascii_words(text: str) -> list[int]:
    """Pack ASCII into 16-bit registers, two characters per register."""
    if len(text) % 2:
        text += "\0"
    return [(ord(text[i]) << 8) | ord(text[i + 1]) for i in range(0, len(text), 2)]


# Raw holding-register words keyed by address; the decoded value is in the comment.
HOLDING: dict[int, int | list[int]] = {
    # -- grid --
    0x14: 230,  # grid voltage / L1 -> 230 V
    0x15: 231,  # L2
    0x16: 229,  # L3
    0x17: 105,  # grid current / L1 -> 10.5 A
    0x18: 110,  # L2 -> 11.0 A
    0x19: 98,  # L3 -> 9.8 A
    0x1A: 4998,  # grid frequency -> 49.98 Hz
    0x21: [0xFFFF, 0xF254],  # active power -> -3500 W (int32)
    0x29: [0, 1200],  # reactive power -> 1200 var (int32)
    # -- battery --
    0x100: 512,  # voltage -> 51.2 V
    0x101: 0xFFEC,  # current -> -2.0 A (int16)
    0x102: 87,  # SOC -> 87 %
    0x119: 132,  # capacity -> 13.2 kWh
    0x120: [0x0001, 0x86A0],  # charged -> 100000 * 0.1 = 10000.0 kWh (uint32)
    0x122: [0x0000, 0x7530],  # discharged -> 3000.0 kWh
    # -- inverter --
    0x400: 231,  # inverter voltage / L1 -> 231 V
    0x401: 232,
    0x402: 233,
    0x403: 100,  # inverter current / L1 -> 10.0 A
    0x404: 101,
    0x405: 102,
    0x406: [0, 700],  # power L1 -> 700 W
    0x408: [0, 720],  # power L2
    0x40A: [0xFFFF, 0xFD44],  # power L3 -> -700 W (int32)
    0x40C: [0, 2140],  # inverter power -> 2140 W
    0x41C: 5001,  # inverter frequency -> 50.01 Hz
    0x435: 352,  # temperature -> 35.2 °C
    0x440: 1,  # run mode -> ONLINE
    # -- EPS --
    0x40E: 228,  # EPS voltage / L1 -> 228 V
    0x40F: 227,
    0x410: 226,
    0x411: 5,  # EPS current / L1 -> 0.5 A
    0x412: 6,
    0x413: 7,
    0x414: [0, 120],  # EPS power L1 -> 120 W
    0x416: [0, 130],
    0x418: [0, 140],
    0x41A: [0, 390],  # EPS power -> 390 W
    # -- PV --
    0x41D: 3005,  # PV 1 voltage -> 300.5 V
    0x41E: 52,  # PV 1 current -> 5.2 A
    0x41F: [0, 1560],  # PV 1 power -> 1560 W
    0x421: 2980,  # PV 2 -> 298.0 V
    0x422: 48,  # 4.8 A
    0x423: [0, 1430],
    0x425: 1500,  # PV 3 -> 150.0 V
    0x426: 20,  # 2.0 A
    0x427: [0, 300],
    # -- identity --
    0x640: ascii_words("V1.23"),  # master software version, 3 of the 5 read
    0x645: ascii_words("SLAVE-2.34"),  # slave version, 5 of the 8 upstream reads
    0x64A: ascii_words("XYZ12345678901234567"),  # serial number, 10 registers
    # -- settings --
    0x805: 2,  # system mode -> HYBRID
    0x811: 1,  # 3-phase unbalance -> enabled
    0x84F: 3,  # time period control -> BOTH_ENABLED
    0x850: 20,  # discharge minimum SOC -> 20 %
    0x851: 1,  # discharge start 1 -> 01:30
    0x852: 5,  # discharge stop 1 -> 05:45
    0x853: 13,  # discharge start 2 -> 13:00
    0x854: 16,  # discharge stop 2 -> 16:15
    0x855: 95,  # charge target SOC -> 95 %
    0x856: 2,  # charge start 1 -> 02:10
    0x857: 4,  # charge stop 1 -> 04:20
    0x858: 14,  # charge start 2 -> 14:00
    0x859: 15,  # charge stop 2 -> 15:30
    0x85A: 30,
    0x85B: 45,
    0x85C: 0,
    0x85D: 15,
    0x85E: 10,
    0x85F: 20,
    0x860: 0,
    0x861: 30,
}


@pytest.fixture
def unit(mock_modbus_unit: MockModbusUnit) -> MockModbusUnit:
    """A mock unit preloaded with the inverter's registers."""
    mock_modbus_unit.holding.update(HOLDING)
    return mock_modbus_unit


@pytest.fixture
def device(unit: MockModbusUnit) -> AlphaESS:
    """A three-phase inverter with EPS and a third MPPT."""
    return AlphaESS(unit, FULL)
