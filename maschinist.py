#!/usr/bin/env python3
"""
Native Instruments Maschine MK2 - USB Raw Data Monitor
Liest HID-Rohdaten direkt vom USB-Geraet.

Installation:
    pip install hidapi
"""

import sys
import time

try:
    import hid
except ImportError:
    print("hidapi nicht gefunden. Bitte installieren:")
    print("   pip install hidapi")
    sys.exit(1)

NI_VENDOR_ID = 0x17CC  # Native Instruments Vendor ID

# Byte index within PAD payload (byte 0 = report ID 0x80, bytes 1-48 = 16 pads × R/G/B).
PAD = {
    # --- Pad row 1 (bottom) ---
    'pad1_r':  1,  'pad1_g':  2,  'pad1_b':  3,
    'pad2_r':  4,  'pad2_g':  5,  'pad2_b':  6,
    'pad3_r':  7,  'pad3_g':  8,  'pad3_b':  9,
    'pad4_r': 10,  'pad4_g': 11,  'pad4_b': 12,
    # --- Pad row 2 ---
    'pad5_r': 13,  'pad5_g': 14,  'pad5_b': 15,
    'pad6_r': 16,  'pad6_g': 17,  'pad6_b': 18,
    'pad7_r': 19,  'pad7_g': 20,  'pad7_b': 21,
    'pad8_r': 22,  'pad8_g': 23,  'pad8_b': 24,
    # --- Pad row 3 ---
    'pad9_r':  25,  'pad9_g':  26,  'pad9_b':  27,
    'pad10_r': 28,  'pad10_g': 29,  'pad10_b': 30,
    'pad11_r': 31,  'pad11_g': 32,  'pad11_b': 33,
    'pad12_r': 34,  'pad12_g': 35,  'pad12_b': 36,
    # --- Pad row 4 (top) ---
    'pad13_r': 37,  'pad13_g': 38,  'pad13_b': 39,
    'pad14_r': 40,  'pad14_g': 41,  'pad14_b': 42,
    'pad15_r': 43,  'pad15_g': 44,  'pad15_b': 45,
    'pad16_r': 46,  'pad16_g': 47,  'pad16_b': 48,
}

def make_pad_payload(**pads):
    """Return a PAD payload list with the given pad colour channels set.

    Usage:
        dev.write(make_pad_payload(pad1_r=0xff))
        dev.write(make_pad_payload(pad13_r=brightness, pad13_g=0x00, pad13_b=0x00))
    """
    payload = [0x80] + [0x00] * 48
    for name, value in pads.items():
        payload[PAD[name]] = value
    return payload

# Byte index within PAYLOAD_BTN for each button (byte 0 = report ID 0x82).
# Fill in the correct index once you've confirmed the mapping via USB sniffing.
BTN = {
    # --- Top left side ---
    'ctrl':       1,
    'step':       2,
    'browse':     3,
    'sampling':   4,
    'back':       5,
    'forward':    6,
    'all':        7,
    'auto':       8,
    # --- User-Buttons on top of device ---
    'user1':      9,
    'user2':    10,
    'user3':     11,
    'user4':     12,
    'user5':     13,
    'user6':     14,
    'user7':     15,
    'user8':     16,
    # --- Main section ---
    'scene':     17,
    'pattern':   18,
    'padmode':   19,
    'navigate':  20,
    'duplicate': 21,
    'select':    22,
    'solo':      23,
    'mute':      24,
    # --- Encoder / misc ---
    'volume':    25,
    'swing':     26,
    'tempo':     27,
    'left':      28,
    'right':     29,
    'enter':     30,
    'noterepeat': 31,
}

# --- Incoming button report (report ID 0x01, 25 bytes total) ---
# Structure: BTN_INPUT[byte_index][bitmask] = button_name
# Example: data[1] == 0x01  →  byte 1, bit 0  →  'user1'
#          data[1] == 0x02  →  byte 1, bit 1  →  'user2'
# Adjust names/masks once confirmed via USB sniffing.
BTN_INPUT = {
    1: {
        0x01: 'user1',
        0x02: 'user2',
        0x04: 'user3',
        0x08: 'user4',
        0x10: 'user5',
        0x20: 'user6',
        0x40: 'user7',
        0x80: 'user8',
    },
    2: {
        0x01: 'ctrl',
        0x02: 'step',
        0x04: 'browse',
        0x08: 'sampling',
        0x10: 'left',
        0x20: 'right',
        0x40: 'all',
        0x80: 'auto',
    },
    3: {
        0x01: 'volume',
        0x02: 'swing',
        0x04: 'tempo',
        0x08: 'left',
        0x10: 'right',
        0x20: 'enter',
        0x40: 'noterepeat',
    },
    4: {
        0x01: 'group_a',
        0x02: 'group_b',
        0x04: 'group_c',
        0x08: 'group_d',
        0x10: 'group_e',
        0x20: 'group_f',
        0x40: 'group_g',
        0x80: 'group_h',
    },
    5:  {
        0x01: 'restart', 
        0x02: 'left', 
        0x04: 'right', 
        0x08: 'grid',
        0x10: 'play',
        0x20: 'rec',
        0x40: 'erase',
        0x80: 'shift'
    },
    6:  {
        0x01: 'scene', 
        0x02: 'pattern', 
        0x04: 'padmode', 
        0x08: 'navigate',
        0x10: 'duplicate',
        0x20: 'select',
        0x40: 'solo',
        0x80: 'mute'
    },

    7:  {0x01: 'unused_7_0', 0x02: 'unused_7_1', 0x04: 'unused_7_2', 0x08: 'unused_7_3',
         0x10: 'unused_7_4', 0x20: 'unused_7_5', 0x40: 'unused_7_6', 0x80: 'unused_7_7'},
    # byte 8:    main encoder  (handled via ENCODER_INPUT, not bitmask)
    # bytes 9+10: encoder 1   (handled via ENCODER_INPUT, not bitmask)
}

# Encoder definitions: name -> (lsb_byte_index, msb_byte_index, max_value)
# msb_byte_index = None for single-byte encoders.
# Value = lsb | (msb << 8), range 0x0000 .. max_value
ENCODER_INPUT = {
    'main_encoder': (8,  None, 0x0F),    # 4-bit single byte, 0x00 .. 0x0F
    'encoder1':     (9,  10,   0x03FF),  # 10-bit, 0x0000 .. 0x03FF
    'encoder2':     (11, 12,   0x03FF),
    'encoder3':     (13, 14,   0x03FF),
    'encoder4':     (15, 16,   0x03FF),
    'encoder5':     (17, 18,   0x03FF),
    'encoder6':     (19, 20,   0x03FF),
    'encoder7':     (21, 22,   0x03FF),
    'encoder8':     (23, 24,   0x03FF),
}

def decode_btn_input(data):
    """Decode a 25-byte button report (report ID 0x01).

    Returns a tuple (pressed, encoders):
        pressed  – list of button names currently held down
        encoders – dict of encoder name -> current value (int)

    Usage:
        data = dev.read(64)
        if data and data[0] == 0x01:
            pressed, encoders = decode_btn_input(data)
            print(pressed)           # e.g. ['user1', 'scene']
            print(encoders)          # e.g. {'encoder1': 512}
    """
    pressed = []
    for byte_idx, masks in BTN_INPUT.items():
        if byte_idx >= len(data):
            break
        byte_val = data[byte_idx]
        for mask, name in masks.items():
            if byte_val & mask:
                pressed.append(name)

    encoders = {}
    for name, (lsb_idx, msb_idx, _) in ENCODER_INPUT.items():
        if lsb_idx < len(data):
            if msb_idx is None:
                encoders[name] = data[lsb_idx]
            elif msb_idx < len(data):
                encoders[name] = data[lsb_idx] | (data[msb_idx] << 8)

    return pressed, encoders


def make_btn_payload(**buttons):
    """Return a PAYLOAD_BTN list with the given buttons set to 0xff.

    Usage:
        dev.write(make_btn_payload(scene=0xff, navigate=0x40))
    """
    payload = [0x82] + [0x00] * 31
    for name, value in buttons.items():
        payload[BTN[name]] = value
    return payload

# Byte index within PAYLOAD_TRANSPORT (byte 0 = report ID 0x81, bytes 1-56).
# Adjust indices once confirmed via USB sniffing.
TRANSPORT = {
    # --- Pads (4x4 grid) ---
    'group_a_r1':        1,
    'group_a_g1':        2,
    'group_a_b1':        3,
    'group_a_r2':        4,
    'group_a_g2':        5,
    'group_a_b2':        6,
    'group_b_r1':        7,
    'group_b_g1':        8,
    'group_b_b1':        9,
    'group_b_r2':       10,
    'group_b_g2':       11,
    'group_b_b2':       12,
    'group_c_r1':       13,
    'group_c_g1':       14,
    'group_c_b1':       15,
    'group_c_r2':       16,
    'group_c_g2':       17,
    'group_c_b2':       18,
    'group_d_r1':       19,
    'group_d_g1':       20,
    'group_d_b1':       21,
    'group_d_r2':       22,
    'group_d_g2':       23,
    'group_d_b2':       24,
    'group_e_r1':       25,
    'group_e_g1':   26,
    'group_e_b1':   27,
    'group_e_r2':   28,
    'group_e_g2':   29,
    'group_e_b2':   30,
    'group_f_r1':   31,
    'group_f_g1':   32,
    'group_f_b1':   33,
    'group_f_r2':   34,
    'group_f_g2':   35,
    'group_f_b2':   36,
    'group_g_r1':   37,
    'group_g_g1':   38,
    'group_g_b1':   39,
    'group_g_r2':   40,
    'group_g_g2':   41,
    'group_g_b2':   42,
    'group_h_r1':   43,
    'group_h_g1':   44,
    'group_h_b1':   45,
    'group_h_r2':   46,
    'group_h_g2':   47,
    'group_h_b2':   48,
    # --- Transport controls ---
    'restart':   49,
    'left':   50,
    'right':   51,
    'grid':   52,
    'play':   53,
    'rec':   54,
    'erase':   55,
    'shift':    56,
}

def make_transport_payload(**items):
    """Return a PAYLOAD_TRANSPORT list with the given entries set.

    Usage:
        dev.write(make_transport_payload(restart=0xff))
        dev.write(make_transport_payload(pad1=0x40, pad2=0x40))
    """
    payload = [0x81] + [0x00] * 56
    for name, value in items.items():
        payload[TRANSPORT[name]] = value
    return payload



def find_devices():
    """Sucht zuerst nach NI-Geraeten, dann alle HID-Geraete."""
    devices = hid.enumerate(NI_VENDOR_ID)
    if not devices:
        devices = hid.enumerate()
    return devices


def select_device(devices):
    """Waehlt automatisch das erste verfuegbare Geraet."""
    if not devices:
        print("Keine HID-Geraete gefunden.")
        sys.exit(1)

    device = devices[0]
    name = device.get("product_string") or "Unbekannt"
    vendor = device.get("manufacturer_string") or ""
    vid = device.get("vendor_id", 0)
    pid = device.get("product_id", 0)
    print(f"\nVerwende: {name} - {vendor}  (VID: {vid:#06x}  PID: {pid:#06x})")
    return device


def format_raw(data):
    """Formatiert Roh-Bytes als HEX + ASCII."""
    hex_str = " ".join(f"{b:02X}" for b in data)
    ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
    return f"HEX: {hex_str:<96}  ASCII: {ascii_str}"


def monitor(device_info):
    """Liest und gibt HID-Rohdaten aus."""
    path = device_info.get("path")
    name = device_info.get("product_string") or "Geraet"

    print(f"\nOeffne: {name}")
    print("Druecke Ctrl+C zum Beenden.\n")
    print("-" * 80)

    try:
        dev = hid.device()
        dev.open_path(path)
        dev.set_nonblocking(True)

        print("Verbunden! Warte auf Daten...\n")
        print(f"  {'Zeit':<12}  Rohdaten")
        print(f"  {'':-<12}  {'':-<60}")

        sent_high = False
        sent_low = False
        while True:
            data = dev.read(64)
            if data and data[0] == 0x20:
                ts = time.strftime("%H:%M:%S.") + f"{int(time.time() * 1000) % 1000:03d}"
                value = (data[25] | (data[26] << 8)) & 0xFFF  # 12-bit value from bytes 26+27
                #print(f"  {ts}  {value}")
                if value > 300 and not sent_high:
                    brightness = int(0.06 * value)
                    dev.write(make_pad_payload(pad13_r=brightness, pad1_g=0xff))
                    #sent_high = True
                    #dev.write(PAYLOAD_TRANSPORT)
                    dev.write(make_btn_payload(tempo=0xff, scene=0x10))
                    dev.write(make_transport_payload(group_a_r1=0xFF, group_a_r2=0xFF))
                    sent_low = False
                elif value < 300 and not sent_low:
                    dev.write(make_pad_payload(pad13_r=0x00))
                    #dev.write(PAYLOAD_TRANSPORT_OFF)
                    dev.write(make_btn_payload(tempo=0x00, scene=0x00))
                    dev.write(make_transport_payload(group_a_r1=0x00, group_a_r2=0x00))
                    sent_low = True
                    sent_high = False
            elif data and data[0] == 0x01:
                pressed = decode_btn_input(data)
                print(pressed)  # e.g. ['user1', 'scene']
            else:
                time.sleep(0.001)

    except OSError as e:
        print(f"\nFehler beim Oeffnen: {e}")
        print("Tipp: Versuche 'sudo python3 usb_monitor.py'")
    except KeyboardInterrupt:
        print("\n\nVerbindung getrennt.")
    finally:
        try:
            dev.close()
        except Exception:
            pass


def main():
    print("\n" + "=" * 55)
    print("  Maschine MK2 - HID Raw Monitor")
    print("=" * 55)

    devices = find_devices()
    device = select_device(devices)
    monitor(device)


if __name__ == "__main__":
    main()