#!/usr/bin/env python3
"""One sheet, every model: score against parameter count, with decode rate below.

The two 4B runs from the earlier field note are first-class points here, so the
whole set can be read at once: what size buys, what quantisation costs, and where
the twelve-gigabyte card stops.
"""

from __future__ import annotations

import math
import sys

from PIL import Image, ImageDraw, ImageFont

from small_models_plate import (INK, MUTED, MONO, MONO_B, OXBLOOD, PAPER, PAPER_DEEP,
                                RULE, SERIF_B, TEAL, _fitted, _title_block, _tracked,
                                paper, stats as _stats)


def stats(slug):
    try:
        return _stats(slug)
    except FileNotFoundError:
        return {}


W, H = 1600, 900

# slug, label, params (B), quant, family
POINTS = [
    ("qwen3-4b", "Qwen3-4B", 4.0, "Q4_K_M", "qwen"),
    ("qwen3-8b", "Qwen3-8B", 8.2, "Q8_0", "qwen"),
    ("qwen3-14b", "Qwen3-14B", 14.8, "Q4_K_M", "qwen"),
    ("gemma3-4b", "Gemma-3-4B", 4.0, "Q4_K_M", "gemma"),
    ("gemma3-12b", "Gemma-3-12B", 12.2, "Q5_K_M", "gemma"),
    ("qwen25-14b", "Qwen2.5-14B", 14.7, "Q4_K_M", "qwen25"),
    ("qwen25coder-7b", "Qwen2.5-Coder-7B", 7.6, "Q8_0", "other"),
    ("llama31-8b", "Llama-3.1-8B", 8.0, "Q8_0", "other"),
    ("mistral-7b", "Mistral-7B", 7.2, "Q8_0", "other"),
    ("deepseek-r1-7b", "R1-Distill-7B", 7.6, "Q8_0", "other"),
]

FAMILY_COLOUR = {"qwen": OXBLOOD, "gemma": TEAL, "qwen25": (86, 104, 66), "other": MUTED}


def render(out: str) -> str:
    img = paper(W, H)
    d = ImageDraw.Draw(img, "RGBA")

    for x in range(40, W - 40, 24):
        d.line([(x, 40), (x, H - 40)], fill=INK + (14 if (x - 40) % 120 == 0 else 7,), width=1)
    for y in range(40, H - 40, 24):
        d.line([(40, y), (W - 40, y)], fill=INK + (14 if (y - 40) % 120 == 0 else 7,), width=1)
    d.rectangle((40, 40, W - 40, H - 40), outline=INK + (210,), width=2)
    d.rectangle((50, 50, W - 50, H - 50), outline=INK + (90,), width=1)

    tracked = lambda xy, txt, font, col, tr: _tracked(d, xy, txt, font, col, tr)

    tracked((86, 70), "COMPARISON SHEET  ·  TEN MODELS  ·  ONE SUITE", ImageFont.truetype(MONO, 18), OXBLOOD, 2.6)
    head = "Does size buy score?"
    f_head = _fitted(d, head, SERIF_B, 64, W - 2 * 88)
    d.text((86, 92), head, font=f_head, fill=INK)
    tracked((88, 92 + f_head.size + 10),
            "CORE-V2: 12 TASKS, 296 CHECKS  ·  LLAMA.CPP  ·  16,384 CTX  ·  EACH MODEL AT THE LARGEST QUANT THAT FITS 12 GB",
            ImageFont.truetype(MONO, 14), MUTED, 1.2)
    d.line([(86, 196), (W - 86, 196)], fill=RULE + (255,), width=2)

    # ---- plot geometry ---------------------------------------------------
    px0, px1 = 168, 1448
    py0, py1 = 248, 616
    xmin, xmax = 3.0, 17.0
    ymin, ymax = 0.0, 0.60

    def sx(p: float) -> float:
        return px0 + (math.log(p) - math.log(xmin)) / (math.log(xmax) - math.log(xmin)) * (px1 - px0)

    def sy(v: float) -> float:
        return py1 - (v - ymin) / (ymax - ymin) * (py1 - py0)

    for v in (0, 10, 20, 30, 40, 50, 60):
        y = sy(v / 100)
        d.line([(px0, y), (px1, y)], fill=INK + (70 if v else 150,), width=1)
        _tracked(d, (px0 - 44, y - 8), f"{v}", ImageFont.truetype(MONO, 13), MUTED, 0.6)
    _tracked(d, (px0 - 44, py0 - 26), "SCORE %", ImageFont.truetype(MONO, 12), INK, 1.4)

    for p in (4, 6, 8, 10, 12, 14, 16):
        x = sx(p)
        d.line([(x, py0), (x, py1)], fill=INK + (26,), width=1)
        _tracked(d, (x - 10, py1 + 8), f"{p}B", ImageFont.truetype(MONO, 13), MUTED, 0.6)
    _tracked(d, (px1 - 84, py1 + 30), "PARAMETERS", ImageFont.truetype(MONO, 12), INK, 1.4)

    d.line([(px0, py1), (px1, py1)], fill=INK + (160,), width=2)
    d.line([(px0, py0), (px0, py1)], fill=INK + (160,), width=2)

    # family guide lines
    groups: dict[str, list] = {}
    for slug, label, params, quant, fam in POINTS:
        groups.setdefault(fam, []).append((params, slug, label, quant))
    for fam, members in groups.items():
        if len(members) < 2:
            continue
        members.sort()
        pts = []
        for params, slug, label, quant in members:
            st = stats(slug)
            if st:
                pts.append((sx(params), sy(st["score"])))
        if len(pts) >= 2:
            d.line(pts, fill=FAMILY_COLOUR[fam] + (120,), width=2)

    # points
    placed = []
    f_lab = ImageFont.truetype(MONO_B, 14)
    f_q = ImageFont.truetype(MONO, 11)
    for slug, label, params, quant, fam in POINTS:
        st = stats(slug)
        if not st:
            continue
        x, y = sx(params), sy(st["score"])
        col = FAMILY_COLOUR[fam]
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=col + (235,), outline=PAPER + (255,), width=2)
        # label above unless crowded, alternate
        dy = -34 if (slug not in ("gemma3-12b", "qwen25-14b")) else 18
        tw = d.textlength(label, font=f_lab)
        d.text((x - tw / 2, y + dy), label, font=f_lab, fill=INK)
        q = f"{st['score']*100:.1f}%  ·  {quant}"
        tw2 = d.textlength(q, font=f_q)
        d.text((x - tw2 / 2, y + dy + 17), q, font=f_q, fill=MUTED)

    # ---- decode strip ----------------------------------------------------
    sy0, sy1 = 706, 784
    d.line([(px0, sy0 - 26), (px1, sy0 - 26)], fill=RULE + (255,), width=1)
    _tracked(d, (px0, sy0 - 46), "DECODE RATE  ·  TOK/S", ImageFont.truetype(MONO, 12), INK, 1.4)
    peak = max((stats(s[0]) or {}).get("tok_s", 0) for s in POINTS) or 1
    bw = 26
    for slug, label, params, quant, fam in POINTS:
        st = stats(slug)
        if not st:
            continue
        x = sx(params)
        h = (st["tok_s"] / peak) * (sy1 - sy0 - 10)
        d.rectangle((x - bw / 2, sy1 - h, x + bw / 2, sy1), fill=FAMILY_COLOUR[fam] + (190,))
        d.text((x - d.textlength(f"{st['tok_s']:.0f}", font=f_q) / 2, sy1 - h - 15),
               f"{st['tok_s']:.0f}", font=f_q, fill=INK)

    # ---- notes -----------------------------------------------------------
    note = ImageFont.truetype(MONO, 13)
    tracked((86, 806), "SAME SUITE, SAME HARNESS: TWELVE CODING TASKS, 296 CHECKS, ONE RUN PER TASK.  FOUR-BILLION POINTS CARRY TWO RUNS EACH.",
            note, MUTED, 0.8)
    tracked((86, 828), "TWELVE TASKS CANNOT RESOLVE A SMALL GAP: ONE TASK IS 8.3 POINTS, SO TREAT NEIGHBOURS AS A TIE.",
            note, MUTED, 0.8)

    _title_block(d, "CMP-001")
    img.save(out)
    return out


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/home/hati/.hermes/cache/scratch/compare.png"
    print(render(out))
