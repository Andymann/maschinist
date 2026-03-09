# Native Instruments Maschine MK2 - HID protocol definitions

# ── Outgoing: pad LEDs (report ID 0x80, 49 bytes) ───────────────────────────
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


# ── Outgoing: button LEDs (report ID 0x82, 32 bytes) ────────────────────────
# Byte index within BTN payload (byte 0 = report ID 0x82).
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
    'user2':     10,
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

def make_btn_payload(**buttons):
    """Return a BTN payload list with the given buttons set.

    Usage:
        dev.write(make_btn_payload(scene=0xff, navigate=0x40))
    """
    payload = [0x82] + [0x00] * 31
    for name, value in buttons.items():
        payload[BTN[name]] = value
    return payload


# ── Outgoing: transport / group LEDs (report ID 0x81, 57 bytes) ─────────────
# Byte index within TRANSPORT payload (byte 0 = report ID 0x81, bytes 1-56).
TRANSPORT = {
    # --- Group button LEDs (A-H, two RGB colours each) ---
    'group_a_r1':  1,  'group_a_g1':  2,  'group_a_b1':  3,
    'group_a_r2':  4,  'group_a_g2':  5,  'group_a_b2':  6,
    'group_b_r1':  7,  'group_b_g1':  8,  'group_b_b1':  9,
    'group_b_r2': 10,  'group_b_g2': 11,  'group_b_b2': 12,
    'group_c_r1': 13,  'group_c_g1': 14,  'group_c_b1': 15,
    'group_c_r2': 16,  'group_c_g2': 17,  'group_c_b2': 18,
    'group_d_r1': 19,  'group_d_g1': 20,  'group_d_b1': 21,
    'group_d_r2': 22,  'group_d_g2': 23,  'group_d_b2': 24,
    'group_e_r1': 25,  'group_e_g1': 26,  'group_e_b1': 27,
    'group_e_r2': 28,  'group_e_g2': 29,  'group_e_b2': 30,
    'group_f_r1': 31,  'group_f_g1': 32,  'group_f_b1': 33,
    'group_f_r2': 34,  'group_f_g2': 35,  'group_f_b2': 36,
    'group_g_r1': 37,  'group_g_g1': 38,  'group_g_b1': 39,
    'group_g_r2': 40,  'group_g_g2': 41,  'group_g_b2': 42,
    'group_h_r1': 43,  'group_h_g1': 44,  'group_h_b1': 45,
    'group_h_r2': 46,  'group_h_g2': 47,  'group_h_b2': 48,
    # --- Transport controls ---
    'restart':    49,
    'left':       50,
    'right':      51,
    'grid':       52,
    'play':       53,
    'rec':        54,
    'erase':      55,
    'shift':      56,
}

def make_transport_payload(**items):
    """Return a TRANSPORT payload list with the given entries set.

    Usage:
        dev.write(make_transport_payload(restart=0xff))
        dev.write(make_transport_payload(group_a_r1=0x40, group_a_r2=0x40))
    """
    payload = [0x81] + [0x00] * 56
    for name, value in items.items():
        payload[TRANSPORT[name]] = value
    return payload


# ── Incoming: button report (report ID 0x01, 25 bytes) ───────────────────────
# BTN_INPUT[byte_index][bitmask] = button_name
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
        0x80: 'main_encoder_press',
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
    5: {
        0x01: 'restart',
        0x02: 'left',
        0x04: 'right',
        0x08: 'grid',
        0x10: 'play',
        0x20: 'rec',
        0x40: 'erase',
        0x80: 'shift',
    },
    6: {
        0x01: 'scene',
        0x02: 'pattern',
        0x04: 'padmode',
        0x08: 'navigate',
        0x10: 'duplicate',
        0x20: 'select',
        0x40: 'solo',
        0x80: 'mute',
    },
    # byte 7:    encoder activity flags (see ENCODER_INPUT, not bitmask buttons)
    # byte 8:    main_encoder value in bits 0-3 (see ENCODER_INPUT)
    # bytes 9+10: encoder1              (see ENCODER_INPUT)
}

# ENCODER_INPUT: name -> (lsb_byte_index, msb_byte_index, max_value)
# msb_byte_index = None for single-byte encoders.
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

    Returns (pressed, encoders):
        pressed  – list of button names currently held down
        encoders – dict of encoder name -> current value (int)

    Usage:
        pressed, encoders = decode_btn_input(data)
        print(pressed)   # e.g. ['user1', 'scene']
        print(encoders)  # e.g. {'encoder1': 512}
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


# ── Incoming: pressure stream (report ID 0x20, 64 bytes) ─────────────────────
# pad_name -> (lsb_byte_index, msb_byte_index)
# 12-bit value = (data[lsb] | (data[msb] << 8)) & 0xFFF, range 0 .. 4095
PRESSURE_INPUT = {
    'pad1':  (25, 26),
    'pad2':  (27, 28),
    'pad3':  (29, 30),
    'pad4':  (31, 32),
    'pad5':  (17, 18),
    'pad6':  (19, 20),
    'pad7':  (21, 22),
    'pad8':  (23, 24),
    'pad9':  ( 9, 10),
    'pad10': (11, 12),
    'pad11': (13, 14),
    'pad12': (15, 16),
    'pad13': ( 1,  2),
    'pad14': ( 3,  4),
    'pad15': ( 5,  6),
    'pad16': ( 7,  8),
}

def decode_pressure_input(data):
    """Decode a 64-byte pressure report (report ID 0x20).

    Returns a dict of pad_name -> pressure value (0 .. 4095).
    Pads with None byte positions are omitted.

    Usage:
        p = decode_pressure_input(data)
        print(p.get('pad13'))  # 0 .. 4095
    """
    result = {}
    for name, (lsb_idx, msb_idx) in PRESSURE_INPUT.items():
        if lsb_idx is None or msb_idx is None:
            continue
        if lsb_idx < len(data) and msb_idx < len(data):
            result[name] = (data[lsb_idx] | (data[msb_idx] << 8)) & 0xFFF
    return result


# ── Outgoing: display (report ID 0xE0/0xE1, 9-byte header + 256-byte chunks) ─
# Buffer layout: 2048 bytes per display (32 bytes/row × 64 rows).
# The display is 256 columns × 64 rows, 1 bit per pixel, row-major, MSB-first.
DISPLAY_ROWS        = 64
DISPLAY_COLS        = 256
DISPLAY_ROW_BYTES   = 32   # 256 columns / 8 bits
DISPLAY_BUFFER_SIZE = DISPLAY_ROW_BYTES * DISPLAY_ROWS  # 2048

def make_display_buffer():
    """Return a blank (all-black) display buffer (2048 bytes)."""
    return bytearray(DISPLAY_BUFFER_SIZE)

def set_pixel(buf, x, y, on=True):
    """Set or clear a pixel at (x, y). x: 0-255, y: 0-63.

    Row-major layout: each row is DISPLAY_ROW_BYTES (32) bytes.
    MSB of each byte = leftmost pixel: mask = 0x80 >> (x & 7)
    """
    if not (0 <= x < DISPLAY_COLS and 0 <= y < DISPLAY_ROWS):
        return
    idx  = DISPLAY_ROW_BYTES * y + (x >> 3)
    mask = 0x80 >> (x & 7)
    if on:
        buf[idx] |= mask
    else:
        buf[idx] &= ~mask

def fill_rect(buf, x, y, w, h, on=True):
    """Fill a rectangle of pixels."""
    for row in range(y, y + h):
        for col in range(x, x + w):
            set_pixel(buf, col, row, on)

def make_display_packets(display_index, buf):
    """Return a list of 8 HID packets that update the full display.

    Each packet is 265 bytes: 9-byte header + 256 bytes of pixel data.

    Usage:
        buf = make_display_buffer()
        set_pixel(buf, 10, 10)
        for pkt in make_display_packets(0, buf):
            dev.write(pkt)
    """
    packets = []
    for chunk in range(8):
        header = [
            0xE0 | display_index,  # report ID + display select
            0x00,
            0x00,
            chunk * 8,             # row offset (0, 8, 16 … 56)
            0x00,
            0x20,                  # 32 columns of controller RAM
            0x00,
            0x08,                  # 8 rows per chunk
            0x00,
        ]
        packets.append(header + list(buf[chunk * 256 : (chunk + 1) * 256]))
    return packets


# ── Text rendering ────────────────────────────────────────────────────────────
# Requires Pillow: pip install Pillow

# Candidate font paths (macOS + Linux). First one that exists is used.
_FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNSDisplay.otf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

def _load_font(size):
    """Return an ImageFont at the given size, falling back to the PIL default."""
    from PIL import ImageFont
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()

def render_text(text, max_width=DISPLAY_COLS, height=DISPLAY_ROWS):
    """Render text as large as possible, centered, into a display buffer.

    Uses draw.textbbox() (Pillow >= 8.0) which reliably accounts for font
    metrics and bearing, so the visible text is truly centred both horizontally
    and vertically.

    Usage:
        buf = render_text("Hello")
        for pkt in make_display_packets(0, buf):
            dev.write(pkt)
    """
    from PIL import Image, ImageDraw

    cx = max_width // 2
    cy = height // 2

    # Binary-search for the largest font size whose visible width fits
    lo, hi = 6, height * 2
    while lo < hi - 1:
        mid = (lo + hi) // 2
        font = _load_font(mid)
        # Use anchor="mm" so bbox is measured relative to the centre point
        bbox = Image.new("1", (1, 1), 0)
        tmp_draw = ImageDraw.Draw(bbox)
        b = tmp_draw.textbbox((0, 0), text, font=font, anchor="mm")
        if b[2] - b[0] <= max_width:
            lo = mid
        else:
            hi = mid

    font = _load_font(lo)

    # Render to a greyscale canvas (avoids mode-"1" quantisation artefacts)
    img = Image.new("L", (max_width, height), 0)
    draw = ImageDraw.Draw(img)
    # anchor="mm" places the visual centre of the text exactly at (cx, cy)
    draw.text((cx, cy), text, font=font, fill=255, anchor="mm")

    # Save a preview PNG next to this file for visual debugging
    import os
    png_path = os.path.join(os.path.dirname(__file__), f"display_preview_{text[:16]}.png")
    img.save(png_path)

    buf = make_display_buffer()
    for py in range(height):
        for px in range(max_width):
            if img.getpixel((px, py)) > 128:
                set_pixel(buf, px, py)
    return buf
