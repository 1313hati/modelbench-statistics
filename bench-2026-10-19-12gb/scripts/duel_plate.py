#!/usr/bin/env python3
"""Paired benchmark sheet: two models, same suite, twelve tasks side by side.

    python3 duel_plate.py 14b out.png

The die is drawn from the GGUF when the weights are still on disk; when they are
not (older runs cleared off the card), the panel shows a hatched plate instead.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from gguf_map import die_image, profile, to_ascii
from small_models_plate import (INK, MUTED, MONO, MONO_B, OXBLOOD, PAPER, PAPER_DEEP,
                                RULE, SERIF, SERIF_B, TEAL, _fitted, _title_block,
                                _tracked, ascii_block, families, gib, paper)

W, H = 1600, 900
MODELS_DIR = Path("/home/hati/.cache/llama-models")
RUNS = Path("/home/hati/.hermes/cache/scratch/smallbench/runs")

META = {
    "qwen3-14b": ("QWEN3-14B", "Qwen3-14B-Q4_K_M.gguf", "Q4_K_M", 14.8),
    "qwen25-14b": ("QWEN2.5-14B-INSTRUCT", "Qwen2.5-14B-Instruct-Q4_K_M.gguf", "Q4_K_M", 14.7),
    "gemma3-12b": ("GEMMA-3-12B-IT", "gemma-3-12b-it-Q5_K_M.gguf", "Q5_K_M", 12.2),
    "gemma3-4b": ("GEMMA-3-4B-IT", "gemma-3-4b-it-Q4_K_M.gguf", "Q4_K_M", 4.3),
    "qwen3-8b": ("QWEN3-8B", "Qwen3-8B-Q8_0.gguf", "Q8_0", 8.2),
    "llama31-8b": ("LLAMA-3.1-8B-INS", "Meta-Llama-3.1-8B-Instruct-Q8_0.gguf", "Q8_0", 8.0),
    "qwen25coder-7b": ("QWEN2.5-CODER-7B", "Qwen2.5-Coder-7B-Instruct-Q8_0.gguf", "Q8_0", 7.6),
    "mistral-7b": ("MISTRAL-7B-V0.3", "Mistral-7B-Instruct-v0.3-Q8_0.gguf", "Q8_0", 7.2),
    "deepseek-r1-7b": ("R1-DISTILL-QWEN-7B", "DeepSeek-R1-Distill-Qwen-7B-Q8_0.gguf", "Q8_0", 7.6),
    "qwen3-4b": ("QWEN3-4B-INS-2507", "Qwen3-4B-Instruct-2507-Q4_K_M.gguf", "Q4_K_M", 4.0),
}

TASKS = [
    ("t01", "weighted jobs"), ("t02", "text justify"), ("t03", "json parser"),
    ("t04", "sql report"), ("t05", "async pool"), ("t06", "repo bugfix"),
    ("t07", "thread queue"), ("t08", "code review"), ("t09", "csv rfc4180"),
    ("t10", "pairs refactor"), ("t11", "varint protocol"), ("t12", "ledger feature"),
]


def load(slug: str) -> dict:
    recs = [json.loads(x) for x in (RUNS / slug / "results.jsonl").read_text().splitlines() if x.strip()]
    per_task: dict[str, list[float]] = {}
    tokens = 0
    for r in recs:
        per_task.setdefault(r["task"], []).append(r["final_score"])
        tokens += (r.get("first") or {}).get("completion_tokens") or 0
    means = {t.split("_")[0]: statistics.mean(v) for t, v in per_task.items()}
    return {
        "score": statistics.mean(means.values()),
        "solved": sum(1 for v in means.values() if v >= 0.999),
        "task": means,
        "tok_task": tokens / max(1, len(recs)),
    }


def hatch(d, box, colour, gap=9):
    x0, y0, x1, y1 = box
    for i in range(int(x0 - (y1 - y0)), int(x1), gap):
        d.line([(max(x0, i), min(y1, y0 + (i - x0))), (min(x1, i + (y1 - y0)), max(y0, y1 - (x1 - i)))],
               fill=colour, width=1)


def column(d, x: int, y: int, slug: str, col: tuple[int, int, int]) -> None:
    label, fname, quant, params = META[slug]
    st = load(slug)
    tracked = lambda xy, txt, f, c, tr: _tracked(d, xy, txt, f, c, tr)

    path = MODELS_DIR / fname
    dw, dh = 272, 228
    if path.exists():
        blocks, _ = profile(str(path))
        rows = to_ascii(die_image(families(blocks), 700, 700), cols=56, gamma=0.78)
        ascii_block(d, 56, x + 12, y + 14, rows, size=8.0, colour=INK, alpha_max=245)
    else:
        for gy in range(y + 14, y + 14 + dh, 12):
            d.line([(x + 12, gy), (x + 12 + dw, gy)], fill=INK + (28,), width=1)
        for gx in range(x + 12, x + 12 + dw, 12):
            d.line([(gx, y + 14), (gx, y + 14 + dh)], fill=INK + (28,), width=1)
        tracked((x + 34, y + 108), "WEIGHTS CLEARED", ImageFont.truetype(MONO, 12), MUTED, 1.6)
    d.rectangle((x + 6, y + 8, x + 8 + dw, y + 8 + dh), outline=col + (150,), width=1)
    d.line([(x + 6, y + 8), (x + 32, y + 8)], fill=col + (255,), width=3)

    tx = x + dw + 36
    tracked((tx, y + 6), label, ImageFont.truetype(MONO_B, 19), INK, 1.2)
    tracked((tx, y + 34), f"{quant}  ·  {gib(str(path)):.2f} GiB  ·  {params:.1f}B" if path.exists()
            else f"{quant}  ·  {params:.1f}B", ImageFont.truetype(MONO, 12), MUTED, 1.0)

    tracked((tx, y + 54), f"{st['score'] * 100:.1f}", ImageFont.truetype(SERIF_B, 66), col, 1.0)
    tracked((tx + 4, y + 140), "% SCORE", ImageFont.truetype(MONO, 11), MUTED, 2.0)

    tracked((tx, y + 176), f"SOLVED {st['solved']}/12", ImageFont.truetype(MONO_B, 15), INK, 1.4)
    tracked((tx, y + 202), f"{st['tok_task']:.0f} completion tok / task", ImageFont.truetype(MONO, 12), MUTED, 0.8)


def render(out: str, a: str, b: str, kicker: str, verdict: str) -> str:
    img = paper(W, H)
    d = ImageDraw.Draw(img, "RGBA")

    for x in range(40, W - 40, 24):
        d.line([(x, 40), (x, H - 40)], fill=INK + (13 if (x - 40) % 120 == 0 else 6,), width=1)
    for y in range(40, H - 40, 24):
        d.line([(40, y), (W - 40, y)], fill=INK + (13 if (y - 40) % 120 == 0 else 6,), width=1)
    d.rectangle((40, 40, W - 40, H - 40), outline=INK + (210,), width=2)
    d.rectangle((50, 50, W - 50, H - 50), outline=INK + (90,), width=1)

    tracked = lambda xy, txt, f, c, tr: _tracked(d, xy, txt, f, c, tr)
    tracked((86, 68), kicker, ImageFont.truetype(MONO, 17), OXBLOOD, 2.6)
    tracked((86, 96), "TWO MODELS  ·  TWELVE TASKS  ·  ONE 12 GB CARD EACH", ImageFont.truetype(MONO, 12), MUTED, 1.8)
    d.line([(86, 128), (W - 86, 128)], fill=INK + (170,), width=1)

    column(d, 86, 150, a, TEAL)
    column(d, 824, 150, b, OXBLOOD)

    # task ledger
    la, lb = load(a), load(b)
    top, rowh = 432, 24
    tracked((86, top - 24), "PER-TASK  —  LEFT: " + META[a][0] + "   ·   RIGHT: " + META[b][0],
            ImageFont.truetype(MONO, 11), MUTED, 1.2)
    d.line([(86, top - 6), (W - 86, top - 6)], fill=RULE + (255,), width=1)

    for i, (key, name) in enumerate(TASKS):
        y = top + i * rowh
        va = la["task"].get(key, 0.0)
        vb = lb["task"].get(key, 0.0)
        tracked((86, y + 3), f"{key}  {name}", ImageFont.truetype(MONO, 12), INK if i % 2 == 0 else MUTED, 0.6)

        ax0, aw = 300, 500
        d.rectangle((ax0, y + 4, ax0 + aw, y + 15), outline=RULE + (200,), width=1)
        d.rectangle((ax0, y + 4, ax0 + max(1, aw * va), y + 15), fill=TEAL + (200,))
        tracked((ax0 + aw + 10, y + 3), f"{va * 100:.0f}", ImageFont.truetype(MONO_B, 12), TEAL, 0.6)

        bx0 = 880
        d.rectangle((bx0, y + 4, bx0 + aw, y + 15), outline=RULE + (200,), width=1)
        d.rectangle((bx0, y + 4, bx0 + max(1, aw * vb), y + 15), fill=OXBLOOD + (200,))
        tracked((bx0 + aw + 10, y + 3), f"{vb * 100:.0f}", ImageFont.truetype(MONO_B, 12), OXBLOOD, 0.6)

    y = top + 12 * rowh + 16
    d.line([(86, y), (W - 86, y)], fill=INK + (170,), width=1)

    size = 30
    while d.textlength(verdict, ImageFont.truetype(SERIF, size)) > W - 480 and size > 18:
        size -= 1
    d.text((86, y + 14), verdict, font=ImageFont.truetype(SERIF, size), fill=INK)

    delta = (la["score"] - lb["score"]) * 100
    tracked((W - 380, y + 20), f"DELTA {delta:+.1f} POINTS", ImageFont.truetype(MONO_B, 15), OXBLOOD, 1.4)

    _title_block(d, {"qwen3-14b": "PT-014", "gemma3-12b": "PT-012", "qwen3-8b": "PT-008", "qwen25coder-7b": "PT-007"}.get(a, "PT-007"))
    img.save(out)
    return out


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "14b":
        render(sys.argv[2], "qwen3-14b", "qwen25-14b",
               "FIELD NOTE  ·  PAIR TEST  ·  14B CLASS",
               "Same size, same weights budget: a thinking pass is worth 39 points.")
    elif which == "gemma":
        render(sys.argv[2], "gemma3-12b", "gemma3-4b",
               "FIELD NOTE  ·  PAIR TEST  ·  GEMMA CLASS",
               "Twice the parameters, the same score to the tenth of a point.")
    elif which == "7b":
        render(sys.argv[2], "qwen25coder-7b", "mistral-7b",
               "FIELD NOTE  ·  PAIR TEST  ·  7B CLASS",
               "A code-tuned 7B scores nearly four times the general 7B.")
    elif which == "8b":
        render(sys.argv[2], "qwen3-8b", "llama31-8b",
               "FIELD NOTE  ·  PAIR TEST  ·  8B CLASS",
               "At eight billion parameters, deliberation decides it.")
    else:
        raise SystemExit("unknown pair")
