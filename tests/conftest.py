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
    0x00: 1,  # grid_meter_ct_enable
    0x01: 1,  # grid_meter_ct_rate
    0x10: [0, 1000],  # total_energy_feed_to_grid
    0x12: [0, 500],  # total_energy_consume_from_grid
    0x14: 230,  # grid voltage / L1 -> 230 V
    0x15: 231,  # L2
    0x16: 229,  # L3
    0x17: 105,  # grid current / L1 -> 10.5 A
    0x18: 110,  # L2 -> 11.0 A
    0x19: 98,  # L3 -> 9.8 A
    0x1A: 4998,  # grid frequency -> 49.98 Hz
    0x1B: [0, 700],  # power_l1
    0x1D: [0, 720],  # power_l2
    0x1F: [0xFFFF, 0xFD44],  # power_l3
    0x21: [0xFFFF, 0xF254],  # active power -> -3500 W (int32)
    0x29: [0, 1200],  # reactive power -> 1200 var (int32)
    0x80: 1,  # meter_ct_enable
    0x81: 1,  # meter_ct_rate
    0x90: [0, 100],  # total_energy_feed_to_grid_pv
    0x94: 230,  # voltage_l1
    0x95: 231,  # voltage_l2
    0x96: 229,  # voltage_l3
    0x97: 10,  # current_l1
    0x98: 11,  # current_l2
    0x99: 12,  # current_l3
    0xA1: [0, 2000],  # active_power_pv_meter
    # -- battery --
    0x100: 512,  # voltage -> 51.2 V
    0x101: 0xFFEC,  # current -> -2.0 A (int16)
    0x102: 87,  # SOC -> 87 %
    0x103: 0,  # status
    0x104: 0,  # relay_status
    0x107: 3300,  # min_cell_voltage -> 3.3 V
    0x10A: 3400,  # max_cell_voltage -> 3.4 V
    0x10D: 250,  # min_cell_temp -> 25.0 °C
    0x110: 280,  # max_cell_temp -> 28.0 °C
    0x111: 100,  # max_charge_current
    0x112: 100,  # max_discharge_current
    0x113: 580,  # charge_cutoff_voltage
    0x114: 450,  # discharge_cutoff_voltage
    0x115: 104,  # BMU software version -> 104
    0x116: 105,  # LMU software version
    0x117: 106,  # ISO software version
    0x118: 2,  # battery_module_count
    0x119: 132,  # capacity -> 13.2 kWh
    0x11A: 1,  # battery_type
    0x11B: 990,  # SOH -> 99.0%
    0x11C: [0, 0],  # battery_warning
    0x11E: [0, 0],  # battery_fault
    0x120: [0x0001, 0x86A0],  # charged -> 100000 * 0.1 = 10000.0 kWh (uint32)
    0x122: [0x0000, 0x7530],  # discharged -> 3000.0 kWh
    0x124: [0x0000, 0x1000],  # total_energy_charge_from_grid
    0x126: 500,  # power
    0x127: 120,  # remaining_time_raw
    0x131: [0, 0],
    0x133: [0, 0],
    0x135: [0, 0],
    0x137: [0, 0],
    0x139: [0, 0],
    0x13B: [0, 0],
    0x13D: [0, 0],
    0x13F: [0, 0],
    0x141: [0, 0],
    0x143: [0, 0],
    0x145: [0, 0],
    0x147: [0, 0],
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
    0x436: [0, 0],
    0x438: [0, 0],
    0x43A: [0, 0],
    0x43C: [0, 0],
    0x43E: [0, 500],  # total_energy_from_pv
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
    0x429: 1500,
    0x42A: 20,
    0x42B: [0, 300],
    0x453: [0, 3000],  # total_power
    # -- system time & EMS version --
    0x740: [0x2605, 0x1307, 0x4712],  # 2026-05-13 07:47:12
    0x743: ascii_words("EMS1234567890123"),  # EMS serial number, 8 registers
    0x74B: [1, 0, 23],  # EMS version -> 1.0.23
    # -- identity --
    0x640: ascii_words("V1.23"),  # master software version, 3 of the 5 read
    0x645: ascii_words("SLAVE-2.34"),  # slave version, 5 of the 8 upstream reads
    0x64A: ascii_words("XYZ12345678901234567"),  # serial number, 10 registers
    # -- settings & network --
    0x800: [0, 5000],  # max_feed_to_grid
    0x801: [0, 6000],  # capacity_storage
    0x803: [0, 6000],  # pv_capacity_grid_inverter
    0x805: 2,  # system mode -> HYBRID
    0x808: 0,  # ip_method -> DHCP
    0x809: [0x0A00, 0x00D1],  # local_ip -> 10.0.0.209
    0x80B: [0xFFFF, 0xFF00],  # subnet_mask -> 255.255.255.0
    0x80D: [0x0A00, 0x0001],  # gateway -> 10.0.0.1
    0x810: 9600,  # modbus_baud_rate
    0x811: 1,  # 3-phase unbalance -> enabled
    0x84F: 3,  # time period control -> BOTH_ENABLED
    0x850: 20,  # discharge minimum SOC -> 20 %
    0x851: 1,
    0x852: 5,
    0x853: 13,
    0x854: 16,
    0x855: 95,
    0x856: 2,
    0x857: 4,
    0x858: 14,
    0x859: 15,
    0x85A: 30,
    0x85B: 45,
    0x85C: 0,
    0x85D: 15,
    0x85E: 10,
    0x85F: 20,
    0x860: 0,
    0x861: 30,
    0x880: 0,
    0x881: [0, 0],
    0x883: [0, 0],
    0x885: 2,
    0x886: 0,
    0x887: 0,
    0x889: 0,
    0x88A: 0,
    0x88F: 0,
    0x890: [0, 0],
    0x8D4: [0, 0],  # system_fault
    0x1000: 1,  # grid_regulation
    0x1002: [0, 0],  # safety_mode_enable
    0x1006: 100,  # pf_value
    0x1007: 2300,  # volt_watt_starting
    0x100A: 5000,  # set_pv_power
    0x100B: 2500,
    0x100C: 100,
    0x100D: 2500,
    0x100E: 600,
    0x100F: 2000,
    0x1010: 100,
    0x1011: 2000,
    0x1012: 100,
    0x1013: 5200,
    0x1014: 100,
    0x1015: 5200,
    0x1016: 100,
    0x1017: 4700,
    0x1018: 100,
    0x1019: 4700,
    0x101A: 100,
    0x101B: 2500,
    0x101C: 100,
    0x101D: 2500,
    0x101E: 100,
    0x101F: 2000,
    0x1020: 100,
    0x1021: 5200,
    0x1022: 100,
    0x1023: 4700,
    0x1024: 100,
    0x1100: 0,  # reset_mode
    0x110E: 1,  # system_language
    # -- BMU --
    0xA000: [0x0001, 0x86A0],  # top BMU sn -> 100000 (uint32)
    0xA00C: 92,  # top BMU soc -> 92%
    0xA200: [0x0002, 0x3456],  # BMU module 1 sn
    0xA205: 520,  # BMU module 1 cluster_voltage -> 52.0 V
    0xA208: 95,  # BMU module 1 soc -> 95%
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
