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

PAYLOAD = [0x80] + [0x00] * 48  # 49 bytes, first byte 0x80

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
    'usder2':    10,
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
    'back':      28,
    'forth':     29,
    'enter':     30,
    'noterepeat': 31,
}

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
                    PAYLOAD[37] = int(0.06 * value) #0xff
                    dev.write(PAYLOAD)
                    #sent_high = True
                    #dev.write(PAYLOAD_TRANSPORT)
                    dev.write(make_btn_payload(tempo=0xff, scene=0x10))
                    dev.write(make_transport_payload(group_a_r1=0xFF, group_a_r2=0xFF))
                    sent_low = False
                elif value < 300 and not sent_low:
                    PAYLOAD[37] = 0x00
                    dev.write(PAYLOAD)
                    #dev.write(PAYLOAD_TRANSPORT_OFF)
                    dev.write(make_btn_payload(tempo=0x00, scene=0x00))
                    dev.write(make_transport_payload(group_a_r1=0x00, group_a_r2=0x00))
                    sent_low = True
                    sent_high = False
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