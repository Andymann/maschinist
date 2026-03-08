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

from maschine_mk2 import (
    make_pad_payload,
    make_btn_payload,
    make_transport_payload,
    decode_btn_input,
    decode_pressure_input,
)

NI_VENDOR_ID = 0x17CC  # Native Instruments Vendor ID


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
                pressure = decode_pressure_input(data)
                value = pressure.get('pad1', 0)
                #print(f"  {ts}  {value}")
                if value > 300 and not sent_high:
                    brightness = int(0.06 * value)
                    dev.write(make_pad_payload(pad13_r=brightness, pad1_g=0xff))
                    #sent_high = True
                    dev.write(make_btn_payload(tempo=0xff, scene=0x10))
                    dev.write(make_transport_payload(group_a_r1=0xFF, group_a_r2=0xFF))
                    sent_low = False
                elif value < 300 and not sent_low:
                    dev.write(make_pad_payload(pad13_r=0x00))
                    dev.write(make_btn_payload(tempo=0x00, scene=0x00))
                    dev.write(make_transport_payload(group_a_r1=0x00, group_a_r2=0x00))
                    sent_low = True
                    sent_high = False
            elif data and data[0] == 0x01:
                pressed, encoders = decode_btn_input(data)
                if pressed:
                    print(f"buttons: {pressed}")
                if any(v for v in encoders.values()):
                    print(f"encoders: {encoders}")
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
