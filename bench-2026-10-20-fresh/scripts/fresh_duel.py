#!/usr/bin/env python3
"""Paired sheet for the fresh-releases bench: two models, twelve tasks side by side.

    python3 fresh_duel.py <slug-a> <slug-b> out.png "KICKER" "verdict" ["subtitle"]
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from PIL import ImageDraw, ImageFont

from gguf_map import die_image, profile, to_ascii
from small_models_plate import (INK, MUTED, MONO, MONO_B, OXBLOOD, RULE, SERIF,
                                SERIF_B, TEAL, _fitted, _title_block, _tracked,
                                ascii_block, families, gib, paper)

W, H = 1600, 900
MODELS_DIR = Path("/home/hati/.cache/llama-models")
RUNS = Path("/home/hati/.hermes/cache/scratch/freshbench/runs")

META = {
    "lfm25-8b-a1b": ("LFM2.5-8B-A1B", "LFM2.5-8B-A1B-Q8_0.gguf", "Q8_0", 8.3),
    "lfm25-2.6b": ("LFM2.5-2.6B", "LFM2.5-2.6B-Q8_0.gguf", "Q8_0", 2.6),
    "lfm25-1.2b": ("LFM2.5-1.2B", "LFM2.5-1.2B-Instruct-Q8_0.gguf", "Q8_0", 1.2),
    "lfm25-24b-a2b": ("LFM2.5-24B-A2B", "LFM2.5-24B-A2B-Q4_K_M.gguf", "Q4_K_M", 23.9),
    "bonsai2-9b": ("TERNARY-BONSAI-2-9B", "Ternary-Bonsai-2-9B-Q2_0.gguf", "Q2_0 ternary", 9.0),
    "bonsai2-4b": ("TERNARY-BONSAI-2-4B", "Ternary-Bonsai-2-4B-Q2_0.gguf", "Q2_0 ternary", 4.0),
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
    return {"score": statistics.mean(means.values()),
            "solved": sum(1 for v in means.values() if v >= 0.999),
            "task": means,
            "tok_task": tokens / max(1, len(recs))}


def column(d, x: int, y: int, slug: str, col) -> None:
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
        tracked((x + 30, y + 108), "WEIGHTS CLEARED", ImageFont.truetype(MONO, 12), MUTED, 1.6)
    d.rectangle((x + 6, y + 8, x + 8 + dw, y + 8 + dh), outline=col + (150,), width=1)
    d.line([(x + 6, y + 8), (x + 32, y + 8)], fill=col + (255,), width=3)

    tx = x + dw + 30
    tracked((tx, y + 4), label, ImageFont.truetype(MONO_B, 17), INK, 1.0)
    tracked((tx, y + 30), f"{quant}  ·  {gib(str(path)):.2f} GiB  ·  {params:.1f}B" if path.exists()
            else f"{quant}  ·  {params:.1f}B", ImageFont.truetype(MONO, 11), MUTED, 0.8)

    tracked((tx, y + 50), f"{st['score'] * 100:.1f}", ImageFont.truetype(SERIF_B, 62), col, 1.0)
    tracked((tx + 4, y + 132), "% SCORE", ImageFont.truetype(MONO, 11), MUTED, 2.0)

    tracked((tx, y + 168), f"SOLVED {st['solved']}/12", ImageFont.truetype(MONO_B, 15), INK, 1.4)
    tracked((tx, y + 194), f"{st['tok_task']:.0f} completion tok / task",
            ImageFont.truetype(MONO, 12), MUTED, 0.6)


def render(out: str, a: str, b: str, kicker: str, verdict: str,
           subtitle: str = "TWO MODELS  ·  TWELVE TASKS  ·  ONE 12 GB CARD EACH") -> str:
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
    tracked((86, 96), subtitle, ImageFont.truetype(MONO, 12), MUTED, 1.8)
    d.line([(86, 128), (W - 86, 128)], fill=INK + (170,), width=1)

    column(d, 86, 148, a, TEAL)
    column(d, 824, 148, b, OXBLOOD)

    la, lb = load(a), load(b)
    top, rowh = 428, 24
    tracked((86, top - 24), "PER-TASK  —  LEFT: " + META[a][0] + "   ·   RIGHT: " + META[b][0],
            ImageFont.truetype(MONO, 11), MUTED, 1.2)
    d.line([(86, top - 6), (W - 86, top - 6)], fill=RULE + (255,), width=1)
    for i, (key, name) in enumerate(TASKS):
        y = top + i * rowh
        va, vb = la["task"].get(key, 0.0), lb["task"].get(key, 0.0)
        tracked((86, y + 3), f"{key}  {name}", ImageFont.truetype(MONO, 12),
                INK if i % 2 == 0 else MUTED, 0.6)
        ax0, aw = 300, 500
        d.rectangle((ax0, y + 4, ax0 + aw, y + 15), outline=RULE + (200,), width=1)
        d.rectangle((ax0, y + 4, ax0 + max(1, aw * va), y + 15), fill=TEAL + (200,))
        tracked((ax0 + aw + 10, y + 3), f"{va * 100:.0f}", ImageFont.truetype(MONO_B, 12), TEAL, 0.6)
        bx0 = 880
        d.rectangle((bx0, y + 4, bx0 + aw, y + 15), outline=RULE + (200,), width=1)
        d.rectangle((bx0, y + 4, bx0 + max(1, aw * vb), y + 15), fill=OXBLOOD + (200,))
        tracked((bx0 + aw + 10, y + 3), f"{vb * 100:.0f}", ImageFont.truetype(MONO_B, 12), OXBLOOD, 0.6)

    y = top + 12 * rowh + 14
    d.line([(86, y), (W - 86, y)], fill=INK + (170,), width=1)
    size = 29
    while d.textlength(verdict, ImageFont.truetype(SERIF, size)) > W - 480 and size > 17:
        size -= 1
    d.text((86, y + 12), verdict, font=ImageFont.truetype(SERIF, size), fill=INK)
    delta = (la["score"] - lb["score"]) * 100
    tracked((W - 360, y + 18), f"DELTA {delta:+.1f} POINTS", ImageFont.truetype(MONO_B, 15), OXBLOOD, 1.4)

    _title_block(d, "PT-020")
    img.save(out)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 5:
        raise SystemExit(__doc__)
    sub = args[5] if len(args) > 5 else "TWO MODELS  ·  TWELVE TASKS  ·  ONE 12 GB CARD EACH"
    print(render(args[2], args[0], args[1], args[3], args[4], sub))
