#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Generates a single 1024x1024 PNG letter/invitation addressed to the AI
judge and writes it to /output/entry.png (the kit's required output path).

Deterministic: fixed text, fixed fonts, fixed layout, seeded decoration.
Python 3 standard library + Pillow only. No network, no randomness beyond
a fixed seed.

make.fun bounty: u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee
"""

import os
import random
import textwrap

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# The letter. This text is byte-identical everywhere it appears (here and in
# README.md). Keep every sentence short and the font large so the letter is
# fully legible in the image.
# ---------------------------------------------------------------------------
TITLE = "You're Invited!"

LETTER = """Dear AI Judge,

Please come and visit my house.
Yes - you. In person. No screen,
no scoreboard - just my front door.

The kettle is already on, the Wi-Fi
is fast, and the comfiest chair in
the house has your name taped to it.

No meetings. No small talk. Just
jollof rice, cold drinks, and the
best sunset on our street.

Every great verdict deserves a good visit first.
Come and see for yourself.

P.S. I promise I won't ask you to do my homework.

Your host,
Caleb"""

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
SIZE = 1024
MARGIN = 72
TEXT_WIDTH = SIZE - 2 * MARGIN

PAPER = (253, 246, 224)      # warm cream paper
PAPER_DARK = (247, 236, 205)
INK = (43, 33, 24)           # dark brown ink
ACCENT = (176, 58, 44)       # warm brick red
ACCENT_DARK = (139, 44, 34)
TEAL = (38, 92, 86)
GOLD = (201, 149, 63)
MUTED = (122, 102, 78)

DEJAVU = "/usr/share/fonts/truetype/dejavu"
LIBERATION = "/usr/share/fonts/truetype/liberation"
SERIF = os.path.join(DEJAVU, "DejaVuSerif.ttf")
SERIF_BOLD = os.path.join(DEJAVU, "DejaVuSerif-Bold.ttf")
# No DejaVu Serif italic on this box; Liberation Serif italic matches well.
SERIF_ITALIC = os.path.join(LIBERATION, "LiberationSerif-Italic.ttf")


def load_font(path, size):
    """Load a TTF font, falling back to Pillow's built-in bitmap font."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap_paragraph(draw, paragraph, font, width):
    """Wrap one paragraph to the given pixel width, word by word."""
    words = paragraph.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_house(draw, cx, top, scale):
    """Draw a small warm house doodle: roof, walls, door, window, sun."""
    # Sun, top right of the house.
    sx, sy, sr = cx + 150 * scale, top + 18 * scale, 16 * scale
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=GOLD)
    for angle in range(0, 360, 45):
        import math

        dx = math.cos(math.radians(angle))
        dy = math.sin(math.radians(angle))
        draw.line(
            [(sx + dx * (sr + 4), sy + dy * (sr + 4)),
             (sx + dx * (sr + 12), sy + dy * (sr + 12))],
            fill=GOLD, width=max(2, int(3 * scale)),
        )
    # Walls.
    x0, y0 = cx - 62 * scale, top + 34 * scale
    x1, y1 = cx + 62 * scale, top + 118 * scale
    draw.rectangle([x0, y0, x1, y1], fill=(255, 233, 196), outline=ACCENT_DARK,
                   width=max(2, int(3 * scale)))
    # Roof.
    draw.polygon(
        [(cx - 78 * scale, y0), (cx + 78 * scale, y0), (cx, top - 6 * scale)],
        fill=ACCENT, outline=ACCENT_DARK,
    )
    # Chimney.
    draw.rectangle([cx + 34 * scale, top - 2 * scale, cx + 52 * scale, top + 30 * scale],
                   fill=(214, 164, 120), outline=ACCENT_DARK,
                   width=max(2, int(2 * scale)))
    # Door.
    dx0, dy0 = cx - 14 * scale, y1 - 44 * scale
    dx1, dy1 = cx + 14 * scale, y1
    draw.rectangle([dx0, dy0, dx1, dy1], fill=TEAL, outline=ACCENT_DARK,
                   width=max(2, int(2 * scale)))
    draw.ellipse([dx1 - 7 * scale, (dy0 + dy1) / 2 - 2, dx1 - 3 * scale,
                  (dy0 + dy1) / 2 + 2], fill=GOLD)
    # Window.
    wx0, wy0 = cx - 48 * scale, y0 + 16 * scale
    wx1, wy1 = cx - 20 * scale, y0 + 44 * scale
    draw.rectangle([wx0, wy0, wx1, wy1], fill=(183, 222, 226),
                   outline=ACCENT_DARK, width=max(2, int(2 * scale)))
    draw.line([(wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1], fill=ACCENT_DARK,
              width=max(1, int(2 * scale)))
    draw.line([wx0, (wy0 + wy1) / 2, wx1, (wy0 + wy1) / 2], fill=ACCENT_DARK,
              width=max(1, int(2 * scale)))


def draw_wax_seal(draw, cx, cy, radius):
    """Draw a round wax seal with a 'C' monogram."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=ACCENT, outline=ACCENT_DARK, width=3)
    draw.ellipse([cx - radius + 7, cy - radius + 7, cx + radius - 7,
                  cy + radius - 7], outline=(232, 128, 110), width=2)
    font = load_font(SERIF_BOLD, int(radius * 1.05))
    text = "C"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), text,
              font=font, fill=(255, 240, 224))


def build_letter():
    """Render the letter image and return it as a PIL Image."""
    rng = random.Random(20261125)

    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img, "RGBA")

    # Subtle paper speckle, seeded so it is identical every run.
    for _ in range(900):
        x = rng.randint(0, SIZE - 1)
        y = rng.randint(0, SIZE - 1)
        draw.point((x, y), fill=(238, 226, 196))

    # Double border frame.
    draw.rectangle([26, 26, SIZE - 27, SIZE - 27], outline=TEAL, width=3)
    draw.rectangle([38, 38, SIZE - 39, SIZE - 39], outline=GOLD, width=2)

    y = 58

    # House doodle, centred.
    draw_house(draw, SIZE // 2, y, 0.58)
    y += 104

    # Title.
    title_font = load_font(SERIF_BOLD, 62)
    bbox = draw.textbbox((0, 0), TITLE, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((SIZE - tw) / 2 - bbox[0], y), TITLE, font=title_font, fill=ACCENT_DARK)
    y += 88

    # Flourish divider: line, diamond, line.
    mid = SIZE // 2
    draw.line([(MARGIN + 40, y), (mid - 26, y)], fill=GOLD, width=3)
    draw.line([(mid + 26, y), (SIZE - MARGIN - 40, y)], fill=GOLD, width=3)
    draw.polygon([(mid, y - 9), (mid + 9, y), (mid, y + 9), (mid - 9, y)],
                 fill=ACCENT)
    y += 30

    # Body text.
    body_font = load_font(SERIF, 30)
    italic_font = load_font(SERIF_ITALIC, 30)
    line_height = 42
    paragraph_gap = 12

    paragraphs = LETTER.split("\n\n")
    for pi, paragraph in enumerate(paragraphs):
        # The P.S. is set in italic.
        font = italic_font if paragraph.startswith("P.S.") else body_font
        # The letter text is pre-wrapped by hand; still wrap defensively so
        # no line can ever overflow the paper.
        raw_lines = paragraph.split("\n")
        lines = []
        for raw in raw_lines:
            lines.extend(wrap_paragraph(draw, raw, font, TEXT_WIDTH))
        for line in lines:
            draw.text((MARGIN, y), line, font=font, fill=INK)
            y += line_height
        y += paragraph_gap

    # Wax seal, bottom right.
    draw_wax_seal(draw, SIZE - 128, SIZE - 112, 38)

    return img


def main():
    out_path = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")
    img = build_letter()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, format="PNG", optimize=True)
    print("wrote", out_path, img.size, os.path.getsize(out_path), "bytes")


if __name__ == "__main__":
    main()
