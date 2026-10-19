#!/usr/bin/env python3
"""Article cover: a 3:1 banner in the same plate register as the bench sheets.

Title on the left, the eight ranked scores as a staircase of rule-filled bars on
the right, dimension lines and a title block. Sized for the X Article cover crop,
so nothing important sits near the vertical edges.

    python3 cover_plate.py out.png
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from small_models_plate import (INK, MUTED, MONO, MONO_B, OXBLOOD, PAPER, PAPER_DEEP,
                                RULE, SERIF_B, TEAL, paper, stats)

W, H = 1800, 640
RUNS = Path("/home/hati/.hermes/cache/scratch/smallbench/runs")

RANK = [
    ("qwen3-14b", "QWEN3-14B", "Q4_K_M"),
    ("qwen3-8b", "QWEN3-8B", "Q8_0"),
    ("qwen25coder-7b", "CODER-7B", "Q8_0"),
    ("gemma3-12b", "GEMMA-12B", "Q5_K_M"),
    ("qwen25-14b", "QWEN2.5-14B", "Q4_K_M"),
    ("llama31-8b", "LLAMA-8B", "Q8_0"),
    ("deepseek-r1-7b", "R1-7B", "Q8_0"),
    ("mistral-7b", "MISTRAL-7B", "Q8_0"),
]


def tracked(d, xy, text, font, fill, spacing=1.6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + spacing
    return x


def main(out: str) -> None:
    img = paper(W, H)
    d = ImageDraw.Draw(img, "RGBA")

    # drafting grid
    for gx in range(0, W, 24):
        d.line([(gx, 0), (gx, H)], fill=INK + (10,), width=1)
    for gy in range(0, H, 24):
        d.line([(0, gy), (W, gy)], fill=INK + (10,), width=1)

    d.rectangle((36, 30, W - 36, H - 30), outline=INK + (120,), width=2)
    d.rectangle((48, 42, W - 48, H - 42), outline=RULE + (110,), width=1)

    tracked(d, (84, 78), "FIELD NOTE  ·  PANEL OF EIGHT  ·  ONE 12 GB CARD",
            ImageFont.truetype(MONO, 15), MUTED, 2.4)

    f_title = ImageFont.truetype(SERIF_B, 92)
    d.text((80, 116), "What fits in", font=f_title, fill=INK)
    d.text((80, 214), "twelve gigabytes", font=f_title, fill=INK)

    f_sub = ImageFont.truetype(MONO, 19)
    d.text((84, 330), "Eight popular models, each fully on one RTX 3060 at 16,384 context,", font=f_sub, fill=INK)
    d.text((84, 360), "largest quantisation that fits. Twelve tasks, 296 checks, one run each.", font=f_sub, fill=INK)

    tracked(d, (84, 424), "BEST SCORE 76.0  ·  WORST 10.6  ·  SPREAD 65.4 POINTS",
            ImageFont.truetype(MONO, 15), OXBLOOD, 1.6)

    # rank bars
    x0, y0 = 1000, 128
    bw, gap = 64, 18
    peak = max((stats(s) or {}).get("score", 0) for s, _, _ in RANK) or 1
    base = 440
    for i, (slug, label, quant) in enumerate(RANK):
        st = stats(slug) or {}
        score = st.get("score", 0)
        h = max(6, int((score / peak) * 240))
        x = x0 + i * (bw + gap)
        d.rectangle((x, base - h, x + bw, base), fill=OXBLOOD + (28,), outline=INK + (110,), width=1)
        for hy in range(base - h + 5, base - 4, 7):
            d.line([(x + 5, hy), (x + bw - 5, hy)], fill=OXBLOOD + (70,), width=1)
        f_num = ImageFont.truetype(SERIF_B, 28)
        txt = f"{score * 100:.1f}"
        d.text((x + bw / 2 - d.textlength(txt, font=f_num) / 2, base - h - 38), txt, font=f_num, fill=INK)
        f_lab = ImageFont.truetype(MONO, 11)
        d.text((x, base + 12), label, font=f_lab, fill=INK)
        d.text((x, base + 28), quant, font=ImageFont.truetype(MONO, 9), fill=MUTED)

    d.line([(x0 - 26, base), (x0 + 8 * (bw + gap) - gap + 8, base)], fill=INK + (150,), width=2)

    # title block
    bx1, by1, bx2, by2 = W - 468, H - 118, W - 96, H - 50
    d.rectangle((bx1, by1, bx2, by2), outline=INK + (150,), width=2)
    d.line([(bx1, by1 + 34), (bx2, by1 + 34)], fill=INK + (110,), width=1)
    d.line([(bx1 + 300, by1), (bx1 + 300, by2)], fill=INK + (110,), width=1)
    tracked(d, (bx1 + 14, by1 + 10), "PANEL EIGHT", ImageFont.truetype(MONO_B, 13), INK, 2.0)
    tracked(d, (bx1 + 14, by1 + 46), "MODELBENCH  ·  FN-005", ImageFont.truetype(MONO, 12), INK, 1.4)
    tracked(d, (bx1 + 14, by1 + 64), "19 OCT 2026", ImageFont.truetype(MONO, 12), MUTED, 1.4)
    tracked(d, (bx1 + 314, by1 + 46), "10 MODELS", ImageFont.truetype(MONO, 12), INK, 1.4)
    tracked(d, (bx1 + 314, by1 + 64), "@1313hati", ImageFont.truetype(MONO, 12), MUTED, 1.4)

    img.save(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
