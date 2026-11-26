"""Thursday 26 November 2026, as a one-page newspaper front page.

Everything on the page is drawn at run time by this program alone. There
is no picture data anywhere in this file: a small bitmap alphabet defined
below, a word wrapper, a few rectangle and rule helpers, and a minimal PNG
writer built on ``struct`` and ``zlib`` turn six short news summaries into
a 1024x1024 PNG. The render is fully deterministic -- run it twice and
the bytes are identical.

Run:  python3 main.py
Out:   $MAKEFUN_OUTPUT_DIR/entry.png   (default /output/entry.png)
"""

import os
import struct
import zlib

PAGE_W = 1024
PAGE_H = 1024

# Palette: cream paper, near-black ink, deep navy masthead, brick red
# kickers, brass rules, white story panels.
PAPER = (247, 243, 232)
INK = (22, 26, 38)
NAVY = (13, 38, 84)
NAVY_LIGHT = (28, 58, 112)
CRIMSON = (172, 32, 32)
BRASS = (196, 158, 74)
PANEL = (255, 255, 255)
EDGE = (198, 192, 178)
MUTED = (92, 96, 108)
PALE_BLUE = (214, 226, 244)

# ---------------------------------------------------------------------------
# Alphabet
#
# A 5-wide, 7-tall bitmap alphabet. Each letter is seven rows of five
# characters; '#' is an inked cell and '.' is empty. The renderer scales
# these cells up, so the same shapes serve every size on the page. All
# copy is upper-cased before drawing, so only capitals are defined here.
# ---------------------------------------------------------------------------

GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".....", ".##..", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "*": (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    "<": ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    ">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
}

CELL_W = 5
CELL_H = 7
CELL_GAP = 1  # one blank column between letters, in cells


def text_width(text, scale):
    """Pixel width of `text` at the given scale, trailing gap excluded."""
    n = len(text)
    if n == 0:
        return 0
    return n * (CELL_W + CELL_GAP) * scale - CELL_GAP * scale


def wrap_words(text, scale, max_width):
    """Greedy word wrap: returns lines that fit inside max_width pixels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Sheet: a plain RGB canvas plus the drawing verbs used by the page.
# ---------------------------------------------------------------------------


class Sheet:
    """An in-memory RGB picture, stored as one flat bytearray."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        self.fill(0, 0, width, height, background)

    def _offset(self, x, y):
        return (y * self.width + x) * 3

    def dot(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            at = self._offset(x, y)
            self.pixels[at] = colour[0]
            self.pixels[at + 1] = colour[1]
            self.pixels[at + 2] = colour[2]

    def fill(self, x, y, w, h, colour):
        """Paint a solid rectangle, clipped to the sheet."""
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        r, g, b = colour
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                at = base + (xx - x0) * 3
                self.pixels[at] = r
                self.pixels[at + 1] = g
                self.pixels[at + 2] = b

    def frame(self, x, y, w, h, colour, thick=2):
        """A hollow rectangle border of the given thickness."""
        self.fill(x, y, w, thick, colour)
        self.fill(x, y + h - thick, w, thick, colour)
        self.fill(x, y, thick, h, colour)
        self.fill(x + w - thick, y, thick, h, colour)

    def rule(self, x, y, w, colour, thick=2):
        self.fill(x, y, w, thick, colour)

    # -- text ---------------------------------------------------------------

    def glyph(self, x, y, char, scale, colour):
        """Stamp one bitmap letter, scaled up by `scale`."""
        rows = GLYPHS.get(char)
        if rows is None:
            return
        for row_i, row in enumerate(rows):
            for col_i, cell in enumerate(row):
                if cell != "#":
                    continue
                self.fill(
                    x + col_i * scale,
                    y + row_i * scale,
                    scale,
                    scale,
                    colour,
                )

    def line(self, x, y, text, scale, colour):
        """Draw one line of text left-aligned at (x, y)."""
        cursor = x
        step = (CELL_W + CELL_GAP) * scale
        for char in text.upper():
            self.glyph(cursor, y, char, scale, colour)
            cursor += step
        return cursor

    def centred(self, y, text, scale, colour, left=0, right=None):
        """Draw one line centred between `left` and `right`."""
        if right is None:
            right = self.width
        wide = text_width(text.upper(), scale)
        start = left + (right - left - wide) // 2
        self.line(start, y, text, scale, colour)

    def paragraph(self, x, y, text, scale, colour, max_width, leading=None):
        """Draw wrapped text; returns the y just below the last line."""
        if leading is None:
            leading = CELL_H * scale + 5
        for row in wrap_words(text, scale, max_width):
            self.line(x, y, row, scale, colour)
            y += leading
        return y


# ---------------------------------------------------------------------------
# PNG writer: signature, IHDR, one IDAT, IEND. No ancillary chunks, no
# timestamps anywhere, so the same picture always encodes to the same
# bytes. zlib level 9 keeps the file small.
# ---------------------------------------------------------------------------


def _chunk(kind, payload):
    size = struct.pack(">I", len(payload))
    crc = struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    return size + kind + payload + crc


def encode_png(sheet):
    header = struct.pack(">IIBBBBB", sheet.width, sheet.height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = sheet.width * 3
    for yy in range(sheet.height):
        raw.append(0)  # filter type 0: no filtering on this scanline
        start = yy * stride
        raw += sheet.pixels[start:start + stride]
    body = zlib.compress(bytes(raw), 9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", body)
        + _chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------------------
# The page itself.
#
# Geometry (1024 x 1024, margin 28):
#   masthead band      y    0 .. 164
#   lead story panel   y  180 .. 452
#   story grid rows    y  468 .. 640, 656 .. 828
#   wide bottom panel  y  844 .. 958
#   footer line        y  972 .. 1004
# ---------------------------------------------------------------------------

MARGIN = 28
GUTTER = 24

LEAD_KICKER = "LEAD STORY  -  TRADE"
LEAD_HEADLINE = "US PROPOSES NEW TARIFFS ON 14 TRADING PARTNERS"
LEAD_BODY = (
    "WASHINGTON HAS PUT FORWARD A NEW ROUND OF TARIFFS COVERING FOURTEEN "
    "TRADING PARTNERS, THE LATEST MOVE IN A WIDENING TRADE DISPUTE THAT HAS "
    "MARKETS AND ALLIES WAITING FOR DETAILS ON RATES, TIMING AND EXEMPTIONS."
)

STORIES = [
    (
        "UKRAINE WAR",
        "TRUMP AND NATO CHIEF URGE RUSSIA NOT TO WIDEN THE WAR",
        "THE US PRESIDENT AND THE NATO SECRETARY GENERAL PRESSED MOSCOW NOT "
        "TO ESCALATE, AS ALLIES WEIGHED THE NEXT STEPS IN SUPPORT FOR KYIV.",
    ),
    (
        "GAZA",
        "ISRAELI STRIKES KILL AT LEAST NINE IN GAZA",
        "AT LEAST NINE PEOPLE WERE KILLED IN ISRAELI STRIKES IN GAZA, "
        "MEDICS AND OFFICIALS SAID, AS THE TOLL OF THE CONFLICT KEPT RISING.",
    ),
    (
        "NORTH KOREA",
        "KIM JONG UN VOWS TO BUILD MORE NUCLEAR WEAPONS",
        "NORTH KOREA'S LEADER SAID THE COUNTRY WOULD KEEP EXPANDING ITS "
        "NUCLEAR ARSENAL, REPEATING A PLEDGE THAT HAS DRAWN CONDEMNATION ABROAD.",
    ),
    (
        "EUROPE",
        "EU SPLIT OVER BUDGET AND $49BN LOAN TO UKRAINE",
        "EU LEADERS REMAINED DIVIDED OVER THE BLOC'S BUDGET AND A PROPOSED "
        "$49 BILLION LOAN TO UKRAINE, LEAVING THE PACKAGE UNSETTLED.",
    ),
    (
        "DISASTERS",
        "BANGKOK OIL DEPOT BLAST AND CAIRO TANKER CRASH",
        "A BLAST AT AN OIL DEPOT IN BANGKOK AND A TANKER CRASH IN CAIRO "
        "CAPPED A DAY OF ACCIDENTS THAT DREW RESCUE CREWS TO BOTH SCENES.",
    ),
]

FOOTER_LEFT = "SOURCES: REUTERS - AP - AFP - AL JAZEERA - SCMP"
FOOTER_RIGHT = "DRAWN AT RUN TIME, NO PHOTOS"


def draw_masthead(sheet):
    sheet.fill(0, 0, PAGE_W, 164, NAVY)
    sheet.fill(0, 0, PAGE_W, 6, BRASS)
    sheet.centred(26, "THE WORLD TODAY", 5, PANEL)
    sheet.rule(352, 76, 320, BRASS, 3)
    sheet.centred(92, "THURSDAY 26 NOVEMBER 2026", 3, BRASS)
    sheet.centred(126, "THE DAY IN SIX STORIES", 2, PALE_BLUE)
    sheet.fill(0, 158, PAGE_W, 6, BRASS)


def draw_lead(sheet):
    x = MARGIN
    y = 180
    w = PAGE_W - 2 * MARGIN
    h = 272
    sheet.fill(x, y, w, h, PANEL)
    sheet.frame(x, y, w, h, INK, 2)
    inner = x + 22
    inner_w = w - 44
    sheet.line(inner, y + 18, LEAD_KICKER, 2, CRIMSON)
    sheet.rule(inner, y + 44, inner_w, EDGE, 2)
    sheet.paragraph(inner, y + 58, LEAD_HEADLINE, 3, INK, inner_w, leading=28)
    sheet.paragraph(inner, y + 100, LEAD_BODY, 2, INK, inner_w, leading=20)
    # Fourteen squares, one per trading partner named in the proposal.
    strip_y = y + 208
    sheet.line(inner, strip_y, "EACH SQUARE IS ONE OF THE FOURTEEN PARTNERS", 2, MUTED)
    box_y = strip_y + 26
    for i in range(14):
        bx = inner + i * 30
        colour = CRIMSON if i % 7 == 3 else NAVY
        sheet.fill(bx, box_y, 22, 22, colour)
        sheet.frame(bx, box_y, 22, 22, BRASS, 1)


def draw_panel(sheet, x, y, w, h, kicker, headline, body):
    sheet.fill(x, y, w, h, PANEL)
    sheet.frame(x, y, w, h, INK, 2)
    inner = x + 18
    inner_w = w - 36
    sheet.line(inner, y + 14, kicker, 2, CRIMSON)
    sheet.rule(inner, y + 38, inner_w, EDGE, 2)
    after_head = sheet.paragraph(inner, y + 50, headline, 2, INK, inner_w, leading=19)
    sheet.paragraph(inner, after_head + 8, body, 2, MUTED, inner_w, leading=19)


def draw_footer(sheet):
    sheet.rule(MARGIN, 972, PAGE_W - 2 * MARGIN, INK, 2)
    sheet.line(MARGIN, 986, FOOTER_LEFT, 2, INK)
    right_w = text_width(FOOTER_RIGHT, 2)
    sheet.line(PAGE_W - MARGIN - right_w, 986, FOOTER_RIGHT, 2, MUTED)


def build_page():
    sheet = Sheet(PAGE_W, PAGE_H, PAPER)
    draw_masthead(sheet)
    draw_lead(sheet)
    col_w = (PAGE_W - 2 * MARGIN - GUTTER) // 2
    rows = [(468, 172), (656, 172)]
    for row_i, (row_y, row_h) in enumerate(rows):
        for col_i in range(2):
            story = STORIES[row_i * 2 + col_i]
            px = MARGIN + col_i * (col_w + GUTTER)
            draw_panel(sheet, px, row_y, col_w, row_h, *story)
    last = STORIES[4]
    draw_panel(sheet, MARGIN, 844, PAGE_W - 2 * MARGIN, 114, *last)
    draw_footer(sheet)
    return sheet


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output/entry.png")
    if out_dir.endswith(".png"):
        out_path = out_dir
        folder = os.path.dirname(out_path) or "."
    else:
        folder = out_dir
        out_path = os.path.join(folder, "entry.png")
    os.makedirs(folder, exist_ok=True)
    data = encode_png(build_page())
    with open(out_path, "wb") as handle:
        handle.write(data)
    print("wrote %s (%d bytes)" % (out_path, len(data)))


if __name__ == "__main__":
    main()
