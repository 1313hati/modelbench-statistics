#!/usr/bin/env python3
"""Eight popular models, each at the best quantisation that fits one 12 GB card.

Paper sheet, specimen cards: every card carries that model's tensor table as a
small ASCII die, its quantisation and weight size, its score, and its decode rate.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from gguf_map import die_image, profile, to_ascii
from small_models_plate import (INK, MUTED, MONO, MONO_B, OXBLOOD, PAPER, PAPER_DEEP,
                                RULE, SERIF_B, TEAL, _fitted, _title_block, _tracked,
                                ascii_block, families, gib, paper, stats as _stats)


def stats(slug):
    try:
        return _stats(slug)
    except FileNotFoundError:
        return {}

W, H = 1600, 900
MODELS_DIR = Path("/home/hati/.cache/llama-models")

CARDS = [
    ("qwen3-14b", "QWEN3-14B", "Qwen3-14B-Q4_K_M.gguf", "Q4_K_M", 14.8),
    ("gemma3-12b", "GEMMA-3-12B-IT", "gemma-3-12b-it-Q5_K_M.gguf", "Q5_K_M", 12.2),
    ("qwen25-14b", "QWEN2.5-14B-INS", "Qwen2.5-14B-Instruct-Q4_K_M.gguf", "Q4_K_M", 14.7),
    ("qwen3-8b", "QWEN3-8B", "Qwen3-8B-Q8_0.gguf", "Q8_0", 8.2),
    ("llama31-8b", "LLAMA-3.1-8B-INS", "Meta-Llama-3.1-8B-Instruct-Q8_0.gguf", "Q8_0", 8.0),
    ("qwen25coder-7b", "QWEN2.5-CODER-7B", "Qwen2.5-Coder-7B-Instruct-Q8_0.gguf", "Q8_0", 7.6),
    ("mistral-7b", "MISTRAL-7B-V0.3", "Mistral-7B-Instruct-v0.3-Q8_0.gguf", "Q8_0", 7.2),
    ("deepseek-r1-7b", "R1-DISTILL-QWEN-7B", "DeepSeek-R1-Distill-Qwen-7B-Q8_0.gguf", "Q8_0", 7.6),
]


def slug_label(slug: str) -> str:
    row = next((c for c in CARDS if c[0] == slug), None)
    return row[1] if row else slug.upper()


def render(out: str, preview: bool = False) -> str:
    img = paper(W, H)
    d = ImageDraw.Draw(img, "RGBA")

    for x in range(40, W - 40, 24):
        d.line([(x, 40), (x, H - 40)], fill=INK + (14 if (x - 40) % 120 == 0 else 7,), width=1)
    for y in range(40, H - 40, 24):
        d.line([(40, y), (W - 40, y)], fill=INK + (14 if (y - 40) % 120 == 0 else 7,), width=1)
    d.rectangle((40, 40, W - 40, H - 40), outline=INK + (210,), width=2)
    d.rectangle((50, 50, W - 50, H - 50), outline=INK + (90,), width=1)

    tracked = lambda xy, txt, font, col, tr: _tracked(d, xy, txt, font, col, tr)

    tracked((86, 70), "FIELD NOTE  ·  EIGHT MODELS  ·  ONE CARD EACH", ImageFont.truetype(MONO, 18), OXBLOOD, 2.6)
    head = "What fits in twelve gigabytes"
    f_head = _fitted(d, head, SERIF_B, 64, W - 2 * 88)
    d.text((86, 94), head, font=f_head, fill=INK)
    tracked((88, 94 + f_head.size + 12),
            "BEST QUANTISATION PER MODEL  ·  16,384 CTX  ·  CORE-V2: 12 TASKS, 296 CHECKS  ·  ONE RUN PER TASK",
            ImageFont.truetype(MONO, 15), MUTED, 1.3)
    d.line([(86, 206), (W - 86, 206)], fill=RULE + (255,), width=2)

    # ---- cards: 2 x 4 ----------------------------------------------------
    cw, ch = 706, 126
    x0s = [86, 86 + cw + 16]
    y0 = 220
    pitch = 136

    for i, (slug, label, fname, quant, params) in enumerate(CARDS):
        col, row = i % 2, i // 2
        cx, cy = x0s[col], y0 + row * pitch
        path = MODELS_DIR / fname
        st = stats(slug)

        # card frame
        d.rectangle((cx, cy, cx + cw, cy + ch), fill=PAPER_DEEP + (70,), outline=RULE + (220,), width=1)

        # die chip
        chip_w, chip_h = 116, 98
        blocks, ts = profile(str(path))
        rows = to_ascii(die_image(families(blocks), 700, 700), cols=32, gamma=1.0)
        ascii_block(d, 32, cx + 13, cy + 14, rows, size=6.0, colour=INK, alpha_max=225)
        d.rectangle((cx + 9, cy + 10, cx + 9 + chip_w, cy + 10 + chip_h), outline=INK + (70,), width=1)

        tx = cx + 9 + chip_w + 20
        _tracked(d, (tx, cy + 12), label, ImageFont.truetype(MONO_B, 18), INK, 1.2)

        size_gib = gib(str(path))
        _tracked(d, (tx, cy + 36), f"{quant}  ·  {size_gib:.2f} GiB  ·  {params:.1f}B", ImageFont.truetype(MONO, 12), MUTED, 1.0)

        if st:
            bar_x0, bar_x1 = tx, cx + cw - 18
            bar_y = cy + 58
            d.rectangle((bar_x0, bar_y, bar_x1, bar_y + 10), fill=INK + (18,))
            frac = max(0.0, min(1.0, st["score"] / 1.0))
            d.rectangle((bar_x0, bar_y, bar_x0 + (bar_x1 - bar_x0) * frac, bar_y + 10), fill=OXBLOOD + (225,))
            _tracked(d, (tx, cy + 74), f"{st['score']*100:.1f}%", ImageFont.truetype(MONO_B, 27), INK, 0.6)
            _tracked(d, (tx + 112, cy + 84),
                     f"{st['solved']}/{st['tasks']} SOLVED  ·  {st['tok_s']:.0f} TOK/S  ·  {st['tok_per_task']:,.0f} TOK/TASK",
                     ImageFont.truetype(MONO, 13), TEAL, 0.8)
        else:
            _tracked(d, (tx, cy + 72), "RUNNING…", ImageFont.truetype(MONO, 15), MUTED, 1.4)

    # ---- footer ----------------------------------------------------------
    d.line([(86, 772), (W - 86, 772)], fill=RULE + (255,), width=1)
    note = ImageFont.truetype(MONO, 13)
    tracked((86, 786), "QUANT IS THE LARGEST THAT LOADS COMPLETELY ON ONE 12 GB CARD AT 16,384 CTX.  LLAMA.CPP, FLASH ATTENTION, KV Q8_0.",
            note, MUTED, 0.8)
    tracked((86, 808), "EACH DIE IS THE MODEL'S OWN TENSOR TABLE: ROWS ARE TENSOR ROLES, COLUMNS ARE BLOCKS, DARKNESS IS SIZE ON DISK.",
            note, MUTED, 0.8)

    _title_block(d, "FN-005")
    img.save(out)
    return out


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/home/hati/.hermes/cache/scratch/panel.png"
    print(render(out))
