#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Monday 23 November 2026.

news-image-20261123 v2: a one-page newspaper front page summing up the
world's news of Monday 23 November 2026. Pure Python standard library:
the PNG encoder, the 5x7 bitmap font and every picture are drawn by this
program itself. No network, no files read, fully deterministic: two runs
write identical bytes to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Layout (1024 x 1024): dark top bar, huge dated masthead, a strapline of
the three biggest stories, a strip of five numbers, a region bar with
story counts, nine numbered picture cards (one per top story), an
"ALSO ON MONDAY" list of ten more stories, a DATE CHECK box that names
other days' news left out on purpose, and a sources footer.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER   = (247, 243, 234)   # warm newsprint
INK     = (20, 33, 61)      # deep navy ink
RED     = (193, 39, 45)     # headline red
TEAL    = (14, 110, 110)
BLUE    = (32, 86, 158)
GOLD    = (176, 124, 22)
GREEN   = (34, 120, 62)
PURPLE  = (96, 62, 140)
BROWN   = (122, 74, 30)
GREY    = (110, 110, 104)
LGREY   = (226, 221, 210)
WHITE   = (255, 255, 255)
BLACK   = (12, 12, 12)
SKY     = (18, 38, 74)      # night-sky banner
SKY2    = (28, 58, 96)
SEA     = (16, 68, 96)
SAND    = (232, 214, 170)

# ------------------------------------------------------------------- font
# 5x7 bitmap font. '#' = ink pixel. Everything is drawn uppercase; the
# table also holds digits and the punctuation this page needs.
FONT = {
 'A': ("01110","10001","10001","11111","10001","10001","10001"),
 'B': ("11110","10001","10001","11110","10001","10001","11110"),
 'C': ("01110","10001","10000","10000","10000","10001","01110"),
 'D': ("11110","10001","10001","10001","10001","10001","11110"),
 'E': ("11111","10000","10000","11110","10000","10000","11111"),
 'F': ("11111","10000","10000","11110","10000","10000","10000"),
 'G': ("01110","10001","10000","10111","10001","10001","01111"),
 'H': ("10001","10001","10001","11111","10001","10001","10001"),
 'I': ("01110","00100","00100","00100","00100","00100","01110"),
 'J': ("00111","00010","00010","00010","00010","10010","01100"),
 'K': ("10001","10010","10100","11000","10100","10010","10001"),
 'L': ("10000","10000","10000","10000","10000","10000","11111"),
 'M': ("10001","11011","10101","10101","10001","10001","10001"),
 'N': ("10001","11001","10101","10011","10001","10001","10001"),
 'O': ("01110","10001","10001","10001","10001","10001","01110"),
 'P': ("11110","10001","10001","11110","10000","10000","10000"),
 'Q': ("01110","10001","10001","10001","10101","10010","01101"),
 'R': ("11110","10001","10001","11110","10100","10010","10001"),
 'S': ("01111","10000","10000","01110","00001","00001","11110"),
 'T': ("11111","00100","00100","00100","00100","00100","00100"),
 'U': ("10001","10001","10001","10001","10001","10001","01110"),
 'V': ("10001","10001","10001","10001","10001","01010","00100"),
 'W': ("10001","10001","10001","10101","10101","10101","01010"),
 'X': ("10001","10001","01010","00100","01010","10001","10001"),
 'Y': ("10001","10001","01010","00100","00100","00100","00100"),
 'Z': ("11111","00001","00010","00100","01000","10000","11111"),
 '0': ("01110","10001","10011","10101","11001","10001","01110"),
 '1': ("00100","01100","00100","00100","00100","00100","01110"),
 '2': ("01110","10001","00001","00110","01000","10000","11111"),
 '3': ("11111","00010","00100","00010","00001","10001","01110"),
 '4': ("00010","00110","01010","10010","11111","00010","00010"),
 '5': ("11111","10000","11110","00001","00001","10001","01110"),
 '6': ("00110","01000","10000","11110","10001","10001","01110"),
 '7': ("11111","00001","00010","00100","01000","01000","01000"),
 '8': ("01110","10001","10001","01110","10001","10001","01110"),
 '9': ("01110","10001","10001","01111","00001","00010","01100"),
 ' ': ("00000","00000","00000","00000","00000","00000","00000"),
 '.': ("00000","00000","00000","00000","00000","01100","01100"),
 ',': ("00000","00000","00000","00000","01100","00100","01000"),
 ':': ("00000","01100","01100","00000","01100","01100","00000"),
 ';': ("00000","01100","01100","00000","01100","00100","01000"),
 "'": ("00100","00100","01000","00000","00000","00000","00000"),
 '-': ("00000","00000","00000","01110","00000","00000","00000"),
 '!': ("00100","00100","00100","00100","00100","00000","00100"),
 '?': ("01110","10001","00001","00110","00100","00000","00100"),
 '(': ("00010","00100","01000","01000","01000","00100","00010"),
 ')': ("01000","00100","00010","00010","00010","00100","01000"),
 '/': ("00001","00010","00010","00100","01000","01000","10000"),
 '%': ("11001","11010","00010","00100","01000","01011","10011"),
 '&': ("01100","10010","10100","01000","10101","10010","01101"),
 '+': ("00000","00100","00100","11111","00100","00100","00000"),
 '=': ("00000","00000","11111","00000","11111","00000","00000"),
 '"': ("01010","01010","00000","00000","00000","00000","00000"),
 '$': ("00100","01111","10100","01110","00101","11110","00100"),
 '>': ("01000","00100","00010","00001","00010","00100","01000"),
 '<': ("00010","00100","01000","10000","01000","00100","00010"),
 '|': ("00100","00100","00100","00100","00100","00100","00100"),
 '*': ("00000","10101","01110","11111","01110","10101","00000"),
}

def text_width(s, scale):
    """Pixel width of s at the given scale (1px gap between glyphs)."""
    if not s:
        return 0
    return len(s) * 6 * scale - scale

def wrap_text(s, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ----------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def triangle(self, p1, p2, p3, c):
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        ymin, ymax = min(y1, y2, y3), max(y1, y2, y3)
        for y in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x1, y1), (x2, y2)),
                                       ((x2, y2), (x3, y3)),
                                       ((x3, y3), (x1, y1))):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by):
                    xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                self.rect(int(min(xs)), y, int(max(xs)) - int(min(xs)) + 1, 1, c)

    def text(self, x, y, s, scale, color, bold=False, align="l"):
        s = s.upper()
        w = text_width(s, scale)
        if align == "c":
            x -= w // 2
        elif align == "r":
            x -= w
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == "1":
                        self.rect(x + col_i * scale, y + row_i * scale,
                                  scale, scale, color)
                        if bold:
                            self.rect(x + col_i * scale + 1,
                                      y + row_i * scale, scale, scale, color)
            x += 6 * scale
        return w

    def text_lines(self, x, y, lines, scale, color, leading=None, bold=False):
        if leading is None:
            leading = 7 * scale + 2
        for line in lines:
            self.text(x, y, line, scale, color, bold=bold)
            y += leading
        return y

# -------------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    rowlen = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * rowlen:(y + 1) * rowlen]

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))

# ------------------------------------------------------- picture banners
# Each banner draws a small scene inside (x, y, w, h). Simple flat shapes
# on a dark sky/sea so the card reads at a glance.

def banner_cop31(cv, x, y, w, h):
    """Climate talks collapse: a cracked globe over a summit table."""
    cv.rect(x, y, w, h, SKY)
    cv.disc(x + 70, y + 34, 26, (52, 140, 120))
    cv.disc(x + 62, y + 26, 9, (90, 170, 110))
    cv.disc(x + 80, y + 42, 7, (90, 170, 110))
    cv.circle(x + 70, y + 34, 26, WHITE)
    cv.line(x + 70, y + 8, x + 70, y + 60, WHITE)
    cv.line(x + 46, y + 34, x + 94, y + 34, WHITE)
    # crack across the globe
    cv.line(x + 58, y + 14, x + 66, y + 28, RED)
    cv.line(x + 66, y + 28, x + 60, y + 42, RED)
    cv.line(x + 60, y + 42, x + 70, y + 56, RED)
    # summit table with empty chairs
    cv.rect(x + 120, y + 44, 180, 5, SAND)
    for cx in range(x + 130, x + 300, 28):
        cv.rect(cx, y + 50, 14, 10, (150, 150, 150))
        cv.rect(cx + 2, y + 38, 10, 8, (200, 200, 200))
    cv.text(x + 150, y + 14, "NO DEAL", 2, RED, bold=True)

def banner_warship(cv, x, y, w, h):
    """Naval drones sink a Russian warship off Libya."""
    cv.rect(x, y, w, h, SKY2)
    for sx in (20, 90, 160, 250):
        cv.disc(x + sx, y + 12, 1, WHITE)
        cv.disc(x + sx + 40, y + 22, 1, WHITE)
    # sea
    cv.rect(x, y + 44, w, h - 44, SEA)
    cv.line(x, y + 46, x + w, y + 46, (90, 160, 200))
    # warship hull + tower
    cv.rect(x + 90, y + 30, 130, 14, (90, 90, 96))
    cv.triangle((x + 90, y + 30), (x + 90, y + 44), (x + 112, y + 44), (90, 90, 96))
    cv.rect(x + 140, y + 16, 26, 14, (70, 70, 76))
    cv.line(x + 153, y + 16, x + 153, y + 6, (200, 200, 200))
    cv.disc(x + 153, y + 5, 2, RED)
    # explosion starburst
    for dx, dy in ((0, -12), (9, -8), (12, 0), (9, 8), (0, 12),
                   (-9, 8), (-12, 0), (-9, -8)):
        cv.line(x + 235, y + 26, x + 235 + dx, y + 26 + dy, GOLD)
    cv.disc(x + 235, y + 26, 5, GOLD)
    # drone boat
    cv.rect(x + 40, y + 48, 22, 5, WHITE)
    cv.line(x + 51, y + 48, x + 90, y + 38, WHITE)

def banner_poland(cv, x, y, w, h):
    """NATO AWACS early-warning aircraft over Poland."""
    cv.rect(x, y, w, h, SKY)
    cv.disc(x + 40, y + 14, 10, (240, 220, 140))
    for sx in (120, 200, 270):
        cv.disc(x + sx, y + 18, 1, WHITE)
    # ground
    cv.rect(x, y + 52, w, 12, (40, 90, 50))
    # AWACS: fuselage + radar disc + tail
    cv.rect(x + 90, y + 26, 130, 10, WHITE)
    cv.triangle((x + 220, y + 26), (x + 220, y + 36), (x + 240, y + 31), WHITE)
    cv.triangle((x + 90, y + 26), (x + 90, y + 36), (x + 74, y + 31), WHITE)
    cv.rect(x + 140, y + 16, 34, 4, WHITE)
    cv.line(x + 157, y + 20, x + 157, y + 26, WHITE)
    cv.rect(x + 100, y + 36, 26, 3, WHITE)
    cv.rect(x + 180, y + 36, 26, 3, WHITE)
    cv.text(x + 232, y + 46, "AWACS", 1, GOLD, bold=True)
    # missile streaks below
    for mx in (60, 150, 250):
        cv.line(x + mx, y + 54, x + mx + 8, y + 62, RED)

def banner_kyiv(cv, x, y, w, h):
    """Russian strikes hit the Kyiv region: skyline, smoke, blast."""
    cv.rect(x, y, w, h, SKY2)
    cv.disc(x + 280, y + 12, 8, (240, 220, 140))
    # skyline
    for bx, bw, bh in ((8, 34, 26), (48, 26, 36), (80, 40, 22),
                       (126, 30, 32), (162, 36, 24), (204, 28, 38)):
        cv.rect(x + bx, y + 52 - bh, bw, bh, (24, 24, 30))
        for wy in range(y + 56 - bh, y + 50, 8):
            cv.rect(x + bx + 5, wy, 4, 4, GOLD)
    # blast + smoke
    cv.disc(x + 235, y + 30, 10, GOLD)
    cv.disc(x + 235, y + 30, 5, RED)
    for dx, dy in ((0, -14), (11, -9), (14, 0), (11, 9), (0, 14),
                   (-11, 9), (-14, 0), (-11, -9)):
        cv.line(x + 235, y + 30, x + 235 + dx, y + 30 + dy, GOLD)
    cv.disc(x + 250, y + 14, 6, (180, 180, 180))
    cv.disc(x + 258, y + 8, 5, (200, 200, 200))

def banner_iran(cv, x, y, w, h):
    """Sanctions on Iran's shadow banking: tanker under a red ban."""
    cv.rect(x, y, w, h, SKY2)
    cv.rect(x, y + 46, w, h - 46, SEA)
    # tanker
    cv.rect(x + 60, y + 30, 150, 16, (160, 60, 50))
    cv.rect(x + 180, y + 14, 30, 16, (200, 200, 200))
    cv.line(x + 195, y + 14, x + 195, y + 6, (200, 200, 200))
    cv.rect(x + 70, y + 22, 130, 8, (120, 40, 36))
    cv.line(x, y + 48, x + w, y + 48, (120, 190, 220))
    # ban circle over the ship
    cv.circle(x + 250, y + 26, 20, RED)
    cv.line(x + 236, y + 40, x + 264, y + 12, RED)
    cv.circle(x + 250, y + 26, 21, RED)

def banner_nvidia(cv, x, y, w, h):
    """Jensen Huang reinstated as Nvidia CEO: chip + rising arrow."""
    cv.rect(x, y, w, h, (16, 40, 28))
    # chip
    cv.rect(x + 96, y + 10, 60, 44, (30, 130, 70))
    cv.rect(x + 108, y + 22, 36, 20, (16, 40, 28))
    cv.text(x + 114, y + 26, "NV", 2, (120, 220, 140), bold=True)
    for px in range(x + 104, x + 150, 12):
        cv.rect(px, y + 4, 4, 6, (120, 220, 140))
        cv.rect(px, y + 54, 4, 6, (120, 220, 140))
    for py in range(y + 18, y + 48, 12):
        cv.rect(x + 90, py, 6, 4, (120, 220, 140))
        cv.rect(x + 156, py, 6, 4, (120, 220, 140))
    # rising arrow
    cv.line(x + 210, y + 52, x + 250, y + 18, (120, 220, 140))
    cv.line(x + 250, y + 18, x + 236, y + 18, (120, 220, 140))
    cv.line(x + 250, y + 18, x + 250, y + 32, (120, 220, 140))
    cv.text(x + 24, y + 18, "CEO", 2, WHITE, bold=True)
    cv.text(x + 24, y + 40, "BACK", 2, (120, 220, 140), bold=True)

def banner_markets(cv, x, y, w, h):
    """AI sell-off: red falling chart over candlesticks."""
    cv.rect(x, y, w, h, (28, 28, 34))
    # grid
    for gx in range(x + 20, x + w, 40):
        cv.vline(gx, y + 6, h - 12, (60, 60, 66))
    for gy in range(y + 10, y + h, 14):
        cv.hline(x + 8, gy, w - 16, (60, 60, 66))
    # candlesticks
    for i, (cx, top, bot, up) in enumerate(((40, 30, 48, False),
                                            (80, 22, 40, False),
                                            (120, 34, 52, True),
                                            (160, 14, 34, False),
                                            (200, 26, 44, False))):
        col = (90, 200, 120) if up else RED
        cv.rect(x + cx, y + top, 14, bot - top, col)
        cv.line(x + cx + 7, y + top - 6, x + cx + 7, y + bot + 6, col)
    # falling line
    pts = [(x + 10, y + 8), (x + 70, y + 20), (x + 130, y + 16),
           (x + 190, y + 34), (x + 250, y + 44), (x + 305, y + 56)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED)
        cv.line(a[0], a[1] + 1, b[0], b[1] + 1, RED)
    cv.text(x + 236, y + 6, "-4%", 2, RED, bold=True)

def banner_fire(cv, x, y, w, h):
    """Sweets-factory fire in Indonesia: factory, flame, smoke."""
    cv.rect(x, y, w, h, (52, 32, 26))
    # factory
    cv.rect(x + 40, y + 30, 150, 26, (140, 130, 120))
    cv.rect(x + 40, y + 22, 150, 8, (110, 100, 92))
    cv.rect(x + 190, y + 12, 14, 44, (110, 100, 92))
    cv.rect(x + 60, y + 38, 12, 10, GOLD)
    cv.rect(x + 90, y + 38, 12, 10, GOLD)
    cv.rect(x + 120, y + 38, 12, 10, GOLD)
    # flame
    cv.triangle((x + 230, y + 56), (x + 250, y + 12), (x + 270, y + 56), GOLD)
    cv.triangle((x + 240, y + 56), (x + 250, y + 28), (x + 260, y + 56), RED)
    cv.triangle((x + 276, y + 56), (x + 286, y + 26), (x + 296, y + 56), GOLD)
    # smoke
    cv.disc(x + 200, y + 8, 6, (170, 170, 170))
    cv.disc(x + 210, y + 4, 5, (190, 190, 190))

def banner_mercury(cv, x, y, w, h):
    """BepiColombo enters orbit around Mercury after eight years."""
    cv.rect(x, y, w, h, BLACK)
    for sx, sy in ((30, 12), (90, 24), (180, 10), (260, 20), (300, 40)):
        cv.disc(x + sx, y + sy, 1, WHITE)
    # orbit ellipse (drawn as a ring of dots)
    for t in range(0, 360, 4):
        import math
        ox = int(150 + 120 * math.cos(math.radians(t)))
        oy = int(34 + 20 * math.sin(math.radians(t)))
        cv.set(x + ox, y + oy, (120, 160, 200))
    # Mercury
    cv.disc(x + 120, y + 34, 22, (170, 160, 150))
    cv.disc(x + 112, y + 28, 4, (140, 130, 120))
    cv.disc(x + 128, y + 40, 5, (140, 130, 120))
    cv.disc(x + 124, y + 24, 3, (150, 140, 130))
    cv.circle(x + 120, y + 34, 22, (220, 210, 200))
    # probe on the orbit
    cv.rect(x + 258, y + 22, 12, 6, WHITE)
    cv.rect(x + 252, y + 24, 6, 2, GOLD)
    cv.rect(x + 270, y + 24, 6, 2, GOLD)
    cv.text(x + 20, y + 50, "8 YEARS", 1, WHITE, bold=True)

# ------------------------------------------------------------- story cards
CARD_W, CARD_H = 317, 190

def card(cv, x, y, num, tag, headline, summary, banner, accent):
    cv.rect(x, y, CARD_W, CARD_H, WHITE)
    banner(cv, x, y, CARD_W, 64)
    cv.rect(x, y + 64, CARD_W, 2, accent)
    cv.text(x + 10, y + 71, str(num), 1, RED, bold=True)
    cv.text(x + 26, y + 71, tag, 1, GREY, bold=True)
    hl = wrap_text(headline, CARD_W - 20, 2)[:2]
    cv.text_lines(x + 10, y + 87, hl, 2, INK, leading=16, bold=True)
    sy = y + 87 + 16 * len(hl) + 4
    sm = wrap_text(summary, CARD_W - 20, 1)
    cv.text_lines(x + 10, sy, sm, 1, (48, 48, 46), leading=9)

STORIES = [
    (1, "ANTALYA, TURKIYE - CLIMATE", "CLIMATE TALKS COLLAPSE",
     "COP31 in Turkiye ends with no deal after record-long talks. "
     "Countries split over fossil-fuel phase-out and adaptation finance.",
     banner_cop31, TEAL),
    (2, "BENGHAZI, LIBYA - WAR", "UKRAINE SINKS RUSSIAN WARSHIP",
     "Naval drones hit the corvette Merkur in port, Kyiv confirms. "
     "A day after a strike on a Russian-linked cargo ship, the war "
     "reaches the Mediterranean.",
     banner_warship, INK),
    (3, "POLAND - NATO", "MISSILES LAND IN POLAND",
     "Three Russian missiles land in Poland, prosecutors say. NATO "
     "sends an AWACS early-warning aircraft to its eastern flank.",
     banner_poland, BLUE),
    (4, "KYIV REGION, UKRAINE - WAR", "STRIKES KILL AT LEAST 15",
     "Russian bombardment hits homes around Kyiv; a boy is pulled alive "
     "from the rubble as rescue teams search on.",
     banner_kyiv, RED),
    (5, "WASHINGTON - IRAN", "IRAN SANCTIONS TIGHTEN",
     "The US Treasury sanctions dozens tied to Iran's shadow banking. "
     "Tehran vows to use all its tools against the US naval blockade.",
     banner_iran, GOLD),
    (6, "CALIFORNIA, USA - TECH", "HUANG BACK AS NVIDIA CEO",
     "Trump reinstates Jensen Huang as CEO and says he poses no "
     "national security threat. SK hynix shares jump 20% on the news.",
     banner_nvidia, GREEN),
    (7, "ASIA - MARKETS", "AI SELL-OFF DEEPENS",
     "Asian tech shares fall further after the Nasdaq AI sell-off. "
     "Bitcoin nears a two-year low, then rebounds to $61,000.",
     banner_markets, RED),
    (8, "CIKANDE, INDONESIA - FIRE", "FACTORY FIRE KILLS 24",
     "A blaze at a sweets factory kills at least 24 people, with about "
     "30 missing. Search teams race to find survivors.",
     banner_fire, BROWN),
    (9, "SPACE - SCIENCE", "MERCURY ORBIT REACHED",
     "BepiColombo enters orbit around Mercury after an eight-year "
     "journey. A pair of spacecraft begin their science mission.",
     banner_mercury, PURPLE),
]

ALSO = [
    "EU PROPOSES 22ND RUSSIA SANCTIONS PACKAGE - VON DER LEYEN",
    "IRANIAN SINGER FLOGGED 74 LASHES WITH HER PRODUCTION TEAM",
    "EURO AREA INFLATION RISES TO 4.0% - EUROSTAT",
    "AI HELPS PROVE THE RIEMANN HYPOTHESIS - ANTHROPIC",
    "NHS TRIALS AI IN BREAST-CANCER SCREENING",
    "DRONE ATTACK IN CUCUTA, COLOMBIA INJURES THREE, INCLUDING AN INFANT",
    "LONDON POLICE SEIZE 893KG OF COCAINE HIDDEN IN ORANGES",
    "BELGIUM FLIGHTS GROUNDED IN STRIKE OVER AUSTERITY",
    "THOUSANDS RALLY IN ISTANBUL AGAINST CRACKDOWN",
    "UN STAFFER KILLED, THREE HURT IN ISRAELI ATTACK ON GAZA",
]

DATE_CHECK = [
    "HONG KONG ELECTION COMMITTEE POLLS - SUN 22 NOV",
    "VERSTAPPEN WINS THE LAS VEGAS GRAND PRIX - SUN 22 NOV",
    "INDIA DECLARE 720/9, A CRICKET RECORD - SUN 22 NOV",
]

REGIONS = [
    ("EUROPE 7", 7, BLUE),
    ("MID EAST 4", 4, RED),
    ("AMERICAS 2", 2, TEAL),
    ("ASIA-PAC 2", 2, GOLD),
    ("AFRICA 1", 1, GREEN),
    ("WORLD 3", 3, PURPLE),
]

NUMBERS = [
    ("0", "CLIMATE DEAL REACHED AT COP31"),
    ("1", "RUSSIAN WARSHIP SUNK OFF LIBYA"),
    ("3", "MISSILES LAND IN POLAND"),
    ("15", "KILLED IN STRIKES AROUND KYIV"),
    ("24", "DEAD IN INDONESIA FACTORY FIRE"),
]

# -------------------------------------------------------------------- page
def build():
    cv = Canvas(W, H, PAPER)

    # top bar
    cv.rect(0, 0, W, 26, INK)
    cv.text(24, 6, "THE WORLD IN ONE DAY", 2, WHITE, bold=True)
    cv.text(1000, 6, "19 STORIES - 6 REGIONS", 2, WHITE, bold=True, align="r")

    # masthead: the day itself, huge
    cv.text(512, 36, "MONDAY 23 NOVEMBER 2026", 6, INK, bold=True, align="c")
    cv.hline(24, 88, 976, INK)
    cv.text(512, 94, "COP31 COLLAPSES - WARSHIP SUNK OFF LIBYA - "
            "MISSILES LAND IN POLAND", 2, RED, bold=True, align="c")

    # number strip: five numbers that tell the day
    y0 = 116
    widths = [195, 195, 195, 195, 196]
    x = 24
    for i, (num, cap) in enumerate(NUMBERS):
        w = widths[i]
        cv.text(x + w // 2, y0, num, 4, RED, bold=True, align="c")
        lines = wrap_text(cap, w - 12, 1)
        ly = y0 + 34
        for line in lines:
            cv.text(x + w // 2, ly, line, 1, INK, align="c")
            ly += 9
        if i < 4:
            cv.vline(x + w, y0 - 2, 56, LGREY)
        x += w
    cv.hline(24, 172, 976, INK)

    # region bar: story counts per region (19 stories in all)
    x = 24
    total = sum(n for _, n, _ in REGIONS)
    for label, n, col in REGIONS:
        w = round(976 * n / total)
        cv.rect(x, 176, w, 20, col)
        cv.text(x + w // 2, 181, label, 1, WHITE, bold=True, align="c")
        x += w

    # nine picture cards
    xs = (24, 353, 682)
    ys = (202, 404, 606)
    for i, story in enumerate(STORIES):
        card(cv, xs[i % 3], ys[i // 3], *story)

    # ALSO panel: ten more stories
    ax, ay, aw = 24, 808, 616
    cv.rect(ax, ay, aw, 144, WHITE)
    cv.rect(ax, ay, aw, 2, RED)
    cv.text(ax + 12, ay + 10, "ALSO ON MONDAY 23 NOVEMBER - 10 MORE STORIES",
            2, INK, bold=True)
    yy = ay + 32
    for item in ALSO:
        cv.text(ax + 12, yy, ">", 1, RED, bold=True)
        cv.text(ax + 26, yy, item, 1, (48, 48, 46))
        yy += 11

    # DATE CHECK panel: other days' news, deliberately left out
    bx, by, bw = 652, 808, 348
    cv.rect(bx, by, bw, 144, WHITE)
    cv.rect(bx, by, bw, 2, RED)
    cv.text(bx + 12, by + 10, "DATE CHECK", 2, RED, bold=True)
    cv.text_lines(bx + 12, by + 32,
                  wrap_text("LEFT OUT AS OTHER DAYS' NEWS:", bw - 24, 1),
                  1, INK, leading=9, bold=True)
    yy = by + 52
    for item in DATE_CHECK:
        cv.text(bx + 12, yy, "-", 1, RED, bold=True)
        lines = wrap_text(item, bw - 40, 1)
        cv.text_lines(bx + 26, yy, lines, 1, (48, 48, 46), leading=9)
        yy += 9 * len(lines) + 2
    cv.text_lines(bx + 12, by + 116,
                  wrap_text("REPORTED = CARRIED BY THE DAY'S WIRES. "
                            "CLAIM = ONE SIDE'S ACCOUNT, LABELLED AS SUCH.",
                            bw - 24, 1),
                  1, GREY, leading=9)

    # sources line
    cv.text(512, 962, "SOURCES: REUTERS, AP, BBC, AL JAZEERA, THE GUARDIAN - "
            "EVERY STORY DATED MONDAY 23 NOVEMBER 2026", 1, GREY, align="c")

    # footer bar
    cv.rect(0, 984, W, 40, INK)
    cv.text(24, 998, "THE WORLD IN ONE DAY", 2, WHITE, bold=True)
    cv.text(1000, 998, "MONDAY 23 NOVEMBER 2026 - ONE PAGE", 2, WHITE,
            bold=True, align="r")
    return cv

def main():
    cv = build()
    data = png_bytes(cv)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o644)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))

if __name__ == "__main__":
    main()
