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
    render_text,
    make_display_packets,
    make_display_buffer,
    render_text_in_area,
    get_area_info,
    AREA_TOTAL,
    encoder_values,
    encoder_names,
)

NI_VENDOR_ID = 0x17CC  # Native Instruments Vendor ID

# encoder name -> (value_area, name_area, index into encoder_values)
ENCODER_AREAS = {
    'encoder1': (9,  5,  0),
    'encoder2': (10, 6,  1),
    'encoder3': (11, 7,  2),
    'encoder4': (12, 8,  3),
    'encoder5': (21, 17, 4),
    'encoder6': (22, 18, 5),
    'encoder7': (23, 19, 6),
    'encoder8': (24, 20, 7),
}

def send_displays(dev):
    """Render text into both displays and send to device."""
    for pkt in make_display_packets(0, render_text("Andyland.info")):
        dev.write(pkt)
    for pkt in make_display_packets(1, render_text("maschinist.mk2")):
        dev.write(pkt)


def apply_encoder_group(area_texts, encoder_values, current_group):
    """Write the current group's names and values into area_texts in place.

    Groups are 0-based; each group covers 8 consecutive values.
    Names come from encoder_names; values from encoder_values.
    """
    for (value_area, name_area, slot) in ENCODER_AREAS.values():
        idx = current_group * 8 + slot
        area_texts[name_area  - 1] = encoder_names[idx]
        area_texts[value_area - 1] = str(encoder_values[idx])


def send_area_texts(dev, area_texts, bufs=None):
    """Render area_texts[0..23] into both displays and send to device.

    area_texts is a 24-element list; index 0 = area 1, index 23 = area 24.
    If bufs is provided (a 2-element list of display buffers), they are cleared
    and updated in place so the caller's buffers stay in sync.
    """
    if bufs is None:
        bufs = [make_display_buffer(), make_display_buffer()]
    else:
        bufs[0][:] = make_display_buffer()
        bufs[1][:] = make_display_buffer()
    for area_num in range(1, 25):
        text = area_texts[area_num - 1]
        display_idx, _, _, _, _ = get_area_info(area_num)
        render_text_in_area(bufs[display_idx], area_num, text)
    for display_idx, buf in enumerate(bufs):
        for pkt in make_display_packets(display_idx, buf):
            dev.write(pkt)


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
        send_displays(dev)
        print(f"  {'Zeit':<12}  Rohdaten")
        print(f"  {'':-<12}  {'':-<60}")

        sent_high = False
        sent_low = False
        prev_pressed = set()
        settings_mode = False
        # Index 0 = area 1, index 23 = area 24
        area_texts = [''] * 24
        current_group = 0
        prev_encoders = {}
        bufs = [make_display_buffer(), make_display_buffer()]

        # Show initial encoder names and values
        apply_encoder_group(area_texts, encoder_values, current_group)
        send_area_texts(dev, area_texts, bufs)

        while True:
            data = dev.read(64)
            if data and data[0] == 0x20:
                if settings_mode:
                    pass  # ignore pad pressure in settings mode
                else:
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
                curr_pressed = set(pressed)

                encoder_held = 'main_encoder_press' in curr_pressed
                if encoder_held != settings_mode:
                    settings_mode = encoder_held
                    print(f"mode: {'settings' if settings_mode else 'operation'}")
                    if settings_mode:
                        area_texts[0]="Hallo"
                        area_texts[7]="Hallo"
                        area_texts[11]="Hallo"
                        area_texts[12]="Hallo"
                    else:
                        area_texts[0]="bye"
                        area_texts[7]="bye"
                        area_texts[11]="du"
                        area_texts[12]="uku"
                    send_area_texts(dev, area_texts, bufs)


                for btn in curr_pressed - prev_pressed:
                    if btn == 'control_left':
                        current_group = max(0, current_group - 1)
                        apply_encoder_group(area_texts, encoder_values, current_group)
                        send_area_texts(dev, area_texts, bufs)
                        prev_encoders.update(encoders)  # discard accumulated raw delta
                        dev.write(make_btn_payload(control_left=0xff))
                        print(f"group: {current_group}")
                    elif btn == 'control_right':
                        current_group = min(15, current_group + 1)
                        apply_encoder_group(area_texts, encoder_values, current_group)
                        send_area_texts(dev, area_texts, bufs)
                        prev_encoders.update(encoders)  # discard accumulated raw delta
                        dev.write(make_btn_payload(control_right=0xff))
                        print(f"group: {current_group}")
                    elif btn == 'shift':
                        dev.write(make_transport_payload(shift=0xff))
                        print(f"pressed:  {btn}")
                    elif btn != 'main_encoder_press':
                        print(f"pressed:  {btn}")
                for btn in prev_pressed - curr_pressed:
                    if btn == 'control_left':
                        dev.write(make_btn_payload(control_left=0x00))
                    elif btn == 'control_right':
                        dev.write(make_btn_payload(control_right=0x00))
                    elif btn == 'shift':
                        dev.write(make_transport_payload(shift=0x00))
                    elif btn != 'main_encoder_press':
                        print(f"released: {btn}")
                prev_pressed = curr_pressed

                dirty_displays = set()
                for name, raw in encoders.items():
                    if name not in ENCODER_AREAS or settings_mode:
                        prev_encoders[name] = raw  # keep in sync, don't compute delta
                        continue
                    value_area, _, slot = ENCODER_AREAS[name]
                    val_idx = current_group * 8 + slot
                    if name in prev_encoders:
                        delta = raw - prev_encoders[name]
                        if delta > 512:
                            delta -= 1024
                        elif delta < -512:
                            delta += 1024
                        if delta:
                            new_val = max(0, min(127, encoder_values[val_idx] + delta))
                            if new_val != encoder_values[val_idx]:
                                encoder_values[val_idx] = new_val
                                area_texts[value_area - 1] = str(new_val)
                                display_idx, _, _, _, _ = get_area_info(value_area)
                                render_text_in_area(bufs[display_idx], value_area, str(new_val))
                                dirty_displays.add(display_idx)
                    prev_encoders[name] = raw

                for display_idx in dirty_displays:
                    for pkt in make_display_packets(display_idx, bufs[display_idx]):
                        dev.write(pkt)
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
