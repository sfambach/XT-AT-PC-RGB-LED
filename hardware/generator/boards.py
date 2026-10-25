# Netlists and placement of the XT-AT-PC-RGB-LED boards (v1 discrete, v2 ATtiny84).
# Used by mksch.py / mkpcb.py / finish.py, see build.sh.
NC = None
R = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical'
D = 'Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_AnodeUp'
C = 'Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm'
TO92 = 'Package_TO_SOT_THT:TO-92_Inline_Wide'
H = 'Connector_PinHeader_2.54mm:PinHeader_1x%02d_P2.54mm_Vertical'
CONN = 'Connector_Generic:Conn_01x%02d'
P = 2.54


def gx(i):
    return round(102.54 + P * i, 3)


def two(ref, value, x0, y, i, kind='R', step=1):
    """2-pin part with pad 1 at column i and pad 2 at column i + step."""
    fp = {'R': R, 'D': D, 'C': C}[kind]
    return fp, ('pads', (gx(i), y), (round(gx(i) + P * step, 3), y))


def header(n, i, y):
    return ('pads', (gx(i), y), (gx(i + 1), y))


# ---------------------------------------------------------------- v1
V1_PARTS = {
    'J1': (CONN % 2, 'PLED', H % 2, (40, 40), {'1': 'PLED_P', '2': 'GND'}),
    'J2': (CONN % 2, 'HDD', H % 2, (40, 70), {'1': NC, '2': 'HDD'}),
    'J3': (CONN % 2, 'TURBO', H % 2, (40, 100), {'1': NC, '2': 'TURBO'}),
    'J4': (CONN % 4, 'RGB LED (A R G B)', H % 4, (250, 70), {'1': 'ANODE', '2': 'RED_K', '3': 'GREEN_K', '4': 'HDD'}),
    'J5': (CONN % 2, 'SW IN', H % 2, (250, 130), {'1': 'SW1', '2': 'SW2'}),
    'J6': (CONN % 2, 'SW OUT', H % 2, (250, 160), {'1': 'SW1', '2': 'SW2'}),
    'R0': ('Device:R', '330 (opt.)', R, (80, 40), {'1': 'PLED_P', '2': 'ANODE'}),
    'R1': ('Device:R', '10k', R, (110, 40), {'1': 'ANODE', '2': 'X1'}),
    'R2': ('Device:R', '10k', R, (170, 40), {'1': 'ANODE', '2': 'X2'}),
    'Q1': ('Transistor_BJT:BC547', 'BC547', TO92, (130, 90), {'1': 'GREEN_K', '2': 'X1', '3': 'E1'}),
    'Q2': ('Transistor_BJT:BC547', 'BC547', TO92, (190, 90), {'1': 'RED_K', '2': 'X2', '3': 'E2'}),
    'D1': ('Diode:1N4148', '1N4148', D, (100, 130), {'1': 'HDD', '2': 'X1'}),
    'D2': ('Diode:1N4148', '1N4148', D, (115, 130), {'1': 'TURBO', '2': 'X1'}),
    'D3': ('Diode:1N4148', '1N4148', D, (160, 130), {'1': 'HDD', '2': 'X2'}),
    'D4': ('Diode:1N4148', '1N4148', D, (130, 130), {'1': 'GND', '2': 'E1'}),
    'D5': ('Diode:1N4148', '1N4148', D, (190, 130), {'1': 'TURBO', '2': 'E2'}),
}
Y1, Y2, YB = 107.4, 112.6, 118.0
V1_PLACE = {
    'J1': header(2, 0, 102.54), 'J2': header(2, 3, 102.54), 'J3': header(2, 6, 102.54),
    'J4': header(4, 0, YB), 'J5': header(2, 5, YB), 'J6': header(2, 8, YB),
    'R0': two('R0', 0, 0, Y1, 0)[1], 'R1': two('R1', 0, 0, Y1, 2.25)[1], 'R2': two('R2', 0, 0, Y1, 4.5)[1],
    'Q2': ('pads', (gx(6.75), Y1), (gx(7.75), Y1)), 'Q1': ('pads', (gx(9.75), Y1), (gx(10.75), Y1)),
    'D1': two('D1', 0, 0, Y2, 0, 'D')[1], 'D2': two('D2', 0, 0, Y2, 2.25, 'D')[1], 'D3': two('D3', 0, 0, Y2, 4.5, 'D')[1],
    'D4': two('D4', 0, 0, Y2, 6.75, 'D')[1], 'D5': two('D5', 0, 0, Y2, 9, 'D')[1],
}
V1 = dict(
    name='xt-at-pc-rgb-led-v1',
    title='XT-AT-PC-RGB-LED v1 - discrete',
    note='Power (green), turbo (red), HDD (blue, priority) on one common anode RGB LED.\n'
         'R0 only if PLED+ has no series resistor on the mainboard, otherwise bridge.\n'
         'github.com/sfambach/XT-AT-PC-RGB-LED - fambach.net',
    power=['GND'],
    board=(93, 100, 141.0, 122.5),
    parts=V1_PARTS, place=V1_PLACE,
    texts=[('PLED + -', gx(0.5), 100.9, 0.8), ('HDD + -', gx(3.5), 100.9, 0.8), ('TURBO + -', gx(6.5), 100.9, 0.8),
           ('A R G B', gx(1.5), 119.75, 0.8), ('SW IN', gx(5.5), 119.75, 0.8), ('SW OUT', gx(8.5), 119.75, 0.8)],
    btexts=[('XT-AT-PC-RGB-LED v1 - fambach.net - CERN-OHL-S-2.0', 117, 121.2, 0.8)],
)

# ---------------------------------------------------------------- v2
U1 = {'1': '+5V', '2': 'DATA_MCU', '3': NC, '4': 'RST', '5': 'PWM_R', '6': 'PWM_G', '7': 'PWM_B', '8': 'MISO', '9': 'SCK',
      '10': 'TB_B', '11': 'TB_A', '12': 'HDD_B', '13': 'HDD_A', '14': 'GND'}
V2_PARTS = {
    'U1': ('MCU_Microchip_ATtiny:ATtiny84A-P', 'ATtiny84A-PU', 'Package_DIP:DIP-14_W7.62mm_Socket', (150, 100), U1),
    'J1': (CONN % 2, '+5V GND', H % 2, (30, 40), {'1': '+5V', '2': 'GND'}),
    'J2': (CONN % 2, 'HDD', H % 2, (30, 80), {'1': 'HDD_A_IN', '2': 'HDD_B_IN'}),
    'J3': (CONN % 2, 'TURBO', H % 2, (30, 120), {'1': 'TB_A_IN', '2': 'TB_B_IN'}),
    'J4': (CONN % 2, 'SW IN', H % 2, (30, 160), {'1': 'SW1', '2': 'SW2'}),
    'J5': (CONN % 2, 'SW OUT', H % 2, (60, 160), {'1': 'SW1', '2': 'SW2'}),
    'J6': (CONN % 3, 'ADDR LED (5V DATA GND)', H % 3, (260, 40), {'1': '+5V', '2': 'DATA', '3': 'GND'}),
    'J7': (CONN % 4, 'RGB LED (COM R G B)', H % 4, (260, 90), {'1': 'COM', '2': 'LED_R', '3': 'LED_G', '4': 'LED_B'}),
    'JP1': (CONN % 3, 'COM: 5V=anode GND=cathode', H % 3, (260, 140), {'1': '+5V', '2': 'COM', '3': 'GND'}),
    'J8': ('Connector:AVR-ISP-6', 'ISP', 'Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical', (210, 160),
           {'1': 'MISO', '2': '+5V', '3': 'SCK', '4': 'PWM_B', '5': 'RST', '6': 'GND'}),
    'R1': ('Device:R', '4k7', R, (70, 60), {'1': 'HDD_A_IN', '2': 'HDD_B_IN'}),
    'R2': ('Device:R', '1k', R, (85, 60), {'1': 'HDD_A_IN', '2': 'HDD_A'}),
    'R3': ('Device:R', '1k', R, (100, 60), {'1': 'HDD_B_IN', '2': 'HDD_B'}),
    'R4': ('Device:R', '4k7', R, (70, 120), {'1': 'TB_A_IN', '2': 'TB_B_IN'}),
    'R5': ('Device:R', '1k', R, (85, 120), {'1': 'TB_A_IN', '2': 'TB_A'}),
    'R6': ('Device:R', '1k', R, (100, 120), {'1': 'TB_B_IN', '2': 'TB_B'}),
    'R7': ('Device:R', '10k', R, (200, 40), {'1': '+5V', '2': 'RST'}),
    'R8': ('Device:R', '330', R, (215, 40), {'1': 'DATA_MCU', '2': 'DATA'}),
    'R9': ('Device:R', '150 (opt.)', R, (215, 80), {'1': 'PWM_R', '2': 'LED_R'}),
    'R10': ('Device:R', '100 (opt.)', R, (215, 100), {'1': 'PWM_G', '2': 'LED_G'}),
    'R11': ('Device:R', '100 (opt.)', R, (215, 120), {'1': 'PWM_B', '2': 'LED_B'}),
    'C1': ('Device:C', '100n', C, (120, 160), {'1': '+5V', '2': 'GND'}),
    'C2': ('Device:C', '100n', C, (140, 160), {'1': '+5V', '2': 'GND'}),
}
YT, YR, YDB, YDT = 102.54, 106.6, 118.6, 110.98
V2_PLACE = {
    'J1': header(2, 0, YT), 'J2': header(2, 3, YT), 'J3': header(2, 6, YT), 'J4': header(2, 9, YT), 'J5': header(2, 12, YT),
    'R1': two('', 0, 0, YR, 0)[1], 'R2': two('', 0, 0, YR, 2.25)[1], 'R3': two('', 0, 0, YR, 4.5)[1],
    'R4': two('', 0, 0, YR, 6.75)[1], 'R5': two('', 0, 0, YR, 9)[1], 'R6': two('', 0, 0, YR, 11.25)[1],
    'R7': two('', 0, 0, YR, 13.5)[1],
    'U1': ('pads', (gx(3), YDB), (gx(4), YDB)),
    'C1': ('pads', (gx(0), 113.5), (round(gx(0) + 2.5, 3), 113.5)),
    'R8': two('', 0, 0, 111.6, 11)[1], 'R9': two('', 0, 0, 111.6, 13.25)[1],
    'R10': two('', 0, 0, 116.6, 11)[1], 'R11': two('', 0, 0, 116.6, 13.25)[1],
    'C2': ('pads', (gx(0), 118.6), (round(gx(0) + 2.5, 3), 118.6)),
    'J6': header(3, 0, 129.0), 'J7': header(4, 4, 129.0), 'JP1': header(3, 9, 126.0),
    'J8': ('pads', (gx(12.5), 123.92), (gx(13.5), 123.92)),
}
V2 = dict(
    name='xt-at-pc-rgb-led-v2',
    title='XT-AT-PC-RGB-LED v2 - ATtiny84',
    note='Inputs: a signal is active when its two header pins differ (load resistor R1/R4 in place of the original LED).\n'
         'J6 addressable LED (APA106/PL9823/WS2812B), J7 plain RGB LED or RGB button, R9-R11 only when J7 is used.\n'
         'JP1: COM to +5V for common anode, to GND for common cathode. J8 standard 6-pin AVR ISP.\n'
         'github.com/sfambach/XT-AT-PC-RGB-LED - fambach.net',
    power=['+5V', 'GND'],
    board=(93, 100, 147.5, 133.0),
    parts=V2_PARTS, place=V2_PLACE,
    texts=[('+5V GND', gx(0.5), 100.9, 0.8), ('HDD', gx(3.5), 100.9, 0.8), ('TURBO', gx(6.5), 100.9, 0.8),
           ('SW IN', gx(9.5), 100.9, 0.8), ('SW OUT', gx(12.5), 100.9, 0.8),
           ('5V D GND', gx(1), 130.6, 0.8), ('COM R G B', gx(5.5), 130.6, 0.8),
           ('A  COM  K', gx(10), 127.6, 0.8), ('ISP', gx(13), 121.9, 0.8)],
    btexts=[('XT-AT-PC-RGB-LED v2 - fambach.net - CERN-OHL-S-2.0', 120.25, 131.9, 0.8)],
)

BOARDS = {'v1': V1, 'v2': V2}
