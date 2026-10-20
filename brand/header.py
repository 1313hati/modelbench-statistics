#!/usr/bin/env python3
"""X profile banner, 1500 x 500 — blueprint register.

`blueprint.py` beside this file is a copy of the toolkit from the
`digital-leonardo-visuals` skill; edit the skill copy first, then re-copy it here.

Regenerate:  python3 brand/header.py brand/header.png
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blueprint as bp  # noqa: E402

W, H = 1500, 500


def title_strip(d: ImageDraw.ImageDraw, w: int, h: int) -> None:
    bw, bh = 372, 62
    x1, y1 = w - 26, h - 26
    x0, y0 = x1 - bw, y1 - bh
    d.rectangle((x0, y0, x1, y1), fill=bp.GROUND + (240,))
    d.rectangle((x0, y0, x1, y1), outline=bp.INK + (210,), width=2)
    d.line((x0, y0 + 30, x1, y0 + 30), fill=bp.INK + (120,), width=1)
    f_big = ImageFont.truetype(bp.MONO_B, 16)
    f_sm = ImageFont.truetype(bp.MONO, 11)
    bp.tracked(d, (x0 + 12, y0 + 8), "MB-STAT 00", f_big, bp.INK, 1.8)
    bp.tracked(d, (x0 + 12, y0 + 38), "LOCAL INFERENCE, MEASURED", f_sm, bp.MUTED, 1.4)
    bp.tracked(d, (x0 + 268, y0 + 38), "@1313hati", f_sm, bp.AMBER, 1.4)


def main(out: str) -> None:
    img = bp.sheet(W, H)
    d = ImageDraw.Draw(img, "RGBA")
    bp.grid(d, W, H, margin=26)
    bp.border(d, W, H, inset=26)
    bp.ruler(d, W, H, inset=26)

    mono = lambda s: ImageFont.truetype(bp.MONO, s)          # noqa: E731
    mono_b = lambda s: ImageFont.truetype(bp.MONO_B, s)      # noqa: E731

    bp.tracked(d, (44, 40), "MODELBENCH · LOCAL INFERENCE DIVISION", mono(13), bp.MUTED, 2.4)

    headline = "WHAT RUNS ON HARDWARE YOU OWN"
    size = 64
    f = ImageFont.truetype(bp.SERIF_B, size)
    while bp.tracked_width(d, headline, f, 1.2) > 1190 and size > 40:
        size -= 2
        f = ImageFont.truetype(bp.SERIF_B, size)
    bp.tracked(d, (44, 66), headline, f, bp.INK, 1.2)
    bp.glow_line(d, [(44, 66 + size + 14), (44 + bp.tracked_width(d, headline, f, 1.2), 66 + size + 14)],
                 bp.CYAN, 1, 120, bloom=7)

    bp.tracked(d, (46, 186), "MODELS THAT FIT ENTIRELY IN 12 GB OF VRAM AT 16K CONTEXT", mono(22), bp.MUTED, 1.8)
    bp.tracked(d, (46, 220), "NO OFFLOAD · NO CLUSTER · NO ESTIMATES", mono(22), bp.MUTED, 1.8)

    readouts = "[ 14 MODELS ]      [ 2 × 12 GB ]      [ 16K CONTEXT ]      [ 0 ESTIMATES ]"
    bp.tracked(d, (46, 288), readouts, mono_b(26), bp.CYAN, 1.6)

    bp.dimension(d, 60, 1460, 372, "MEASURED ON THE HARDWARE PEOPLE ALREADY HAVE", mono(14), bp.CYAN)

    bp.tracked(d, (700, 436), "GITHUB.COM/1313HATI", mono(15), bp.MUTED, 1.6)

    title_strip(d, W, H)
    img.save(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "header.png")
