#!/usr/bin/env python3
"""news-image-20261126 -- a newspaper front page, drawn entirely in code.

Entry for the make.fun bounty "news-image-20261126".  Running this file
renders a 1024x1024 PNG front page that sums up the world news of
Thursday 26 November 2026: the date in large type, the day's lead story
and five more panels, each with a short summary checked against that
day's reporting (Reuters, AP, AFP, Al Jazeera, SCMP).

No image data is embedded anywhere in this program.  Every pixel of the
front page is drawn at run time by the code below: a hand-defined 5x7
bitmap font, a small word-wrapping typesetter, and a minimal PNG writer
built on the standard library alone (os, struct, zlib), so it runs in
any plain Python 3 sandbox with no third-party packages.

Output: $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
The render is deterministic -- same code, same bytes, every run.
"""

import os
import struct
import zlib

# ------------------------------------------------------------------ page

WIDTH = 1024
HEIGHT = 1024

BG = (8, 22, 48)            # deep blue page background
PANEL = (14, 34, 66)        # slightly lighter panel fill
PANEL_EDGE = (96, 122, 165)  # panel border
FRAME = (150, 168, 198)     # outer frame line
INK = (236, 240, 247)       # off-white main text
MUTED = (168, 182, 205)     # grey-blue secondary text
GOLD = (240, 190, 70)       # accent: masthead rule, kickers

# ------------------------------------------------------------------ font
# A 5x7 bitmap font, defined by hand below.  Each glyph is seven rows of
# five pixels, written as "0"/"1" strings so the letterforms stay easy to
# read (and to fix) in the source.  The typesetter scales glyphs by an
# integer factor, so headlines are just the same font drawn bigger.

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "10001", "11001", "10101", "10011", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01101", "10011", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "10001", "01111", "00001"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}

# Characters the font does not carry are folded onto close equivalents
# before typesetting, so copy can be written naturally.
FOLD = {
    "\u2019": "'",   # right single quote -> apostrophe
    "\u2018": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2014": "-",   # em dash -> hyphen
    "\u2013": "-",
}


def fold_text(text):
    """Replace characters outside the bitmap font with equivalents."""
    out = []
    for ch in text:
        if ch in FONT:
            out.append(ch)
        elif ch in FOLD:
            out.append(FOLD[ch])
        else:
            out.append(" ")
    return "".join(out)


# --------------------------------------------------------------- drawing

GLYPH_W = 5
GLYPH_H = 7
ADVANCE = 6  # glyph width plus one pixel of letter spacing, in font units


def text_width(text, scale):
    """Pixel width of a string at the given integer scale."""
    if not text:
        return 0
    return len(text) * ADVANCE * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap: split text into lines that fit max_width."""
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


class Canvas:
    """A flat RGB pixel buffer with just the drawing we need."""

    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.px = bytearray(bytes(color) * (width * height))

    def fill_rect(self, x, y, w, h, color):
        """Fill a rectangle, clipped to the canvas."""
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            start = (yy * self.width + x0) * 3
            self.px[start:start + len(row)] = row

    def frame_rect(self, x, y, w, h, color, thick):
        """Draw a rectangular outline of the given thickness."""
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def draw_char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "1":
                    self.fill_rect(x + col_i * scale, y + row_i * scale,
                                   scale, scale, color)

    def draw_text(self, x, y, text, scale, color):
        """Draw one line of text with its top-left corner at (x, y)."""
        cx = x
        for ch in fold_text(text):
            self.draw_char(cx, y, ch, scale, color)
            cx += ADVANCE * scale
        return cx

    def draw_text_centered(self, y, text, scale, color):
        x = (self.width - text_width(fold_text(text), scale)) // 2
        self.draw_text(x, y, text, scale, color)

    def draw_block(self, x, y, lines, scale, leading, color):
        """Draw pre-wrapped lines top to bottom; return the end y."""
        cy = y
        for line in lines:
            self.draw_text(x, cy, line, scale, color)
            cy += leading
        return cy


def draw_panel(canvas, x, y, w, h):
    """A news panel: filled box with a thin lighter border."""
    canvas.fill_rect(x, y, w, h, PANEL)
    canvas.frame_rect(x, y, w, h, PANEL_EDGE, 2)


# --------------------------------------------------------------- content
# The day's six stories, as reported on Thursday 26 November 2026 and
# checked against Reuters, AP, AFP, Al Jazeera and SCMP coverage.

LEAD_HEADLINE = "US proposes new tariffs on 14 trading partners"
LEAD_BODY = (
    "The US trade office proposed new duties on goods from China, "
    "the EU, Japan, India and ten more partners, blaming excess "
    "factory output. Brazil faces a surprise 10% duty on aircraft."
)

STORIES = [
    (
        "Trump and NATO chief urge Russia not to widen the war",
        "Trump and NATO chief Rutte, after talks in Florida, said "
        "Russia must avoid widening the Ukraine war; Trump posted "
        "that Putin should pull back.",
    ),
    (
        "Israeli strikes kill at least nine in Gaza",
        "Israeli strikes and gunfire killed at least nine "
        "Palestinians overnight, among them a Hamas-appointed "
        "deputy minister, despite the ceasefire.",
    ),
    (
        "Kim Jong Un vows to build more nuclear weapons",
        "North Korea's Kim showed off nuclear warheads and vowed "
        "to expand the arsenal after snubbing Trump's offer of "
        "talks.",
    ),
    (
        "EU split over budget and $49bn loan to Ukraine",
        "EU leaders split over the budget and a $49 billion loan "
        "to Ukraine, and picked Spain's Pablo Hernandez de Cos as "
        "the next ECB chief.",
    ),
    (
        "Bangkok oil depot blast injures nine; Cairo crash kills 31",
        "A blast and fire at a Bangkok oil depot injured at least "
        "nine; in Cairo, a tanker crash killed 31 and the driver "
        "was detained.",
    ),
]

FOOTER_SOURCES = "Sources: Reuters, AP, AFP, Al Jazeera, SCMP"
FOOTER_NOTE = "Every story checked against that day's reporting."

# ---------------------------------------------------------------- layout

MARGIN = 48          # left/right edge of the content column
INNER = MARGIN + 16  # text inset inside a panel
TEXT_W = WIDTH - 2 * INNER

HEAD_SCALE = 3       # panel headlines
HEAD_LEAD = 27
BODY_SCALE = 2       # panel body copy
BODY_LEAD = 19
PANEL_PAD = 12       # vertical padding inside a panel


def block_height(lines, scale, leading):
    """Pixel height of a wrapped text block: the first line's glyph
    height plus one leading step for each further line."""
    return GLYPH_H * scale + (lines - 1) * leading


def panel_height(head_lines, body_lines):
    return (PANEL_PAD + block_height(head_lines, HEAD_SCALE, HEAD_LEAD)
            + 6 + block_height(body_lines, BODY_SCALE, BODY_LEAD)
            + PANEL_PAD)


def draw_story(canvas, y, headline, body):
    """Draw one story panel at vertical position y; return its height."""
    head_lines = wrap_text(headline, HEAD_SCALE, TEXT_W)
    body_lines = wrap_text(body, BODY_SCALE, TEXT_W)
    h = panel_height(len(head_lines), len(body_lines))
    draw_panel(canvas, MARGIN, y, WIDTH - 2 * MARGIN, h)
    cy = y + PANEL_PAD
    cy = canvas.draw_block(INNER, cy, head_lines, HEAD_SCALE, HEAD_LEAD, INK)
    cy += 6
    canvas.draw_block(INNER, cy, body_lines, BODY_SCALE, BODY_LEAD, MUTED)
    return h


def draw_front_page():
    canvas = Canvas(WIDTH, HEIGHT, BG)
    canvas.frame_rect(24, 24, WIDTH - 48, HEIGHT - 48, FRAME, 3)

    # Masthead: paper name, then the date in large type, then rules.
    canvas.draw_text_centered(44, "THE WORLD TODAY", 3, GOLD)
    canvas.draw_text_centered(76, "THURSDAY 26 NOVEMBER 2026", 5, INK)
    canvas.fill_rect(MARGIN, 124, WIDTH - 2 * MARGIN, 3, GOLD)
    canvas.fill_rect(MARGIN, 131, WIDTH - 2 * MARGIN, 1, PANEL_EDGE)

    y = 148

    # Lead story: gold kicker, a bigger headline, three lines of body.
    lead_head = wrap_text(LEAD_HEADLINE, 4, TEXT_W)
    lead_body = wrap_text(LEAD_BODY, BODY_SCALE, TEXT_W)
    lead_h = (14 + GLYPH_H * BODY_SCALE + 8
              + (GLYPH_H * 4 + (len(lead_head) - 1) * 36) + 8
              + (GLYPH_H * BODY_SCALE + (len(lead_body) - 1) * BODY_LEAD)
              + 14)
    draw_panel(canvas, MARGIN, y, WIDTH - 2 * MARGIN, lead_h)
    cy = y + 14
    canvas.draw_text(INNER, cy, "LEAD STORY", BODY_SCALE, GOLD)
    cy += GLYPH_H * BODY_SCALE + 8
    cy = canvas.draw_block(INNER, cy, lead_head, 4, 36, INK)
    cy += 8
    canvas.draw_block(INNER, cy, lead_body, BODY_SCALE, BODY_LEAD, MUTED)
    y += lead_h + 10

    # The other five stories, one panel each, stacked down the page.
    for headline, body in STORIES:
        y += draw_story(canvas, y, headline, body) + 8

    # Footer: where the stories came from.
    canvas.draw_text_centered(y + 8, FOOTER_SOURCES, BODY_SCALE, INK)
    canvas.draw_text_centered(y + 32, FOOTER_NOTE, BODY_SCALE, MUTED)
    return canvas


# ------------------------------------------------------------ PNG output

def png_chunk(tag, data):
    chunk = struct.pack(">I", len(data)) + tag + data
    chunk += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return chunk


def encode_png(canvas):
    """Encode the canvas as a PNG byte string (RGB, no interlace)."""
    raw = bytearray()
    stride = canvas.width * 3
    for yy in range(canvas.height):
        raw.append(0)  # filter type 0 (None) on every scanline
        start = yy * stride
        raw += canvas.px[start:start + stride]
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height,
                       8, 2, 0, 0, 0)  # 8-bit RGB
    return (b"\x89PNG\r\n\x1a\n"
            + png_chunk(b"IHDR", ihdr)
            + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + png_chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(draw_front_page())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
