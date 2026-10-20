#!/usr/bin/env python3
"""One-model sheet for a single bench: die profile, score, twelve task bars.

    python3 fresh_solo.py <slug> out.png "KICKER" "verdict line"
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
    "lfm25-8b-a1b": ("LFM2.5-8B-A1B", "LFM2.5-8B-A1B-Q8_0.gguf", "Q8_0  ·  8.3B TOTAL  ·  1B ACTIVE", "ONE 12 GB CARD"),
    "lfm25-2.6b": ("LFM2.5-2.6B", "LFM2.5-2.6B-Q8_0.gguf", "Q8_0  ·  2.6B", "ONE 12 GB CARD"),
    "lfm25-1.2b": ("LFM2.5-1.2B-INSTRUCT", "LFM2.5-1.2B-Instruct-Q8_0.gguf", "Q8_0  ·  1.2B", "ONE 12 GB CARD"),
    "lfm25-24b-a2b": ("LFM2.5-24B-A2B", "LFM2.5-24B-A2B-Q4_K_M.gguf", "Q4_K_M  ·  23.9B TOTAL  ·  2B ACTIVE", "BOTH CARDS"),
    "bonsai2-9b": ("TERNARY-BONSAI-2-9B", "Ternary-Bonsai-2-9B-Q2_0.gguf", "Q2_0 TERNARY  ·  9B", "ONE 12 GB CARD"),
    "bonsai2-4b": ("TERNARY-BONSAI-2-4B", "Ternary-Bonsai-2-4B-Q2_0.gguf", "Q2_0 TERNARY  ·  4B", "ONE 12 GB CARD"),
}

TASKS = [
    ("t01", "weighted job scheduler"), ("t02", "text justification"),
    ("t03", "json parser"), ("t04", "sql report"), ("t05", "async worker pool"),
    ("t06", "repo bugfix"), ("t07", "thread-safe queue"), ("t08", "code review"),
    ("t09", "csv rfc 4180"), ("t10", "pairs refactor"), ("t11", "varint protocol"),
    ("t12", "ledger feature"),
]


def load(slug: str) -> dict:
    recs = [json.loads(x) for x in (RUNS / slug / "results.jsonl").read_text().splitlines() if x.strip()]
    per: dict[str, list[float]] = {}
    toks = 0
    rates = []
    for r in recs:
        per.setdefault(r["task"], []).append(r["final_score"])
        for phase in ("first", "repair"):
            ph = r.get(phase) or {}
            toks += (ph.get("prompt_tokens") or 0) + (ph.get("completion_tokens") or 0)
            if ph.get("tok_per_s"):
                rates.append(ph["tok_per_s"])
    means = {t.split("_")[0]: statistics.mean(v) for t, v in per.items()}
    return {"score": statistics.mean(means.values()),
            "solved": sum(1 for v in means.values() if v >= 0.999),
            "task": means,
            "tok_s": statistics.median(rates) if rates else 0.0,
            "tok_task": toks / max(1, len(recs)),
            "tasks": len(means)}


def render(out: str, slug: str, kicker: str, verdict: str) -> str:
    label, fname, quant, place = META[slug]
    st = load(slug)
    path = MODELS_DIR / fname

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
    tracked((86, 96), f"CORE-V2  ·  TWELVE TASKS  ·  296 CHECKS  ·  {place}  ·  16,384 CTX",
            ImageFont.truetype(MONO, 12), MUTED, 1.8)
    d.line([(86, 128), (W - 86, 128)], fill=INK + (170,), width=1)

    # die profile
    dw, dh = 440, 292
    if path.exists():
        blocks, _ = profile(str(path))
        rows = to_ascii(die_image(families(blocks), 900, 620), cols=84, gamma=0.8)
        ascii_block(d, 84, 84, 152, rows, size=7.9, colour=INK, alpha_max=245)
    d.rectangle((80, 146, 80 + dw, 146 + dh), outline=TEAL + (120,), width=1)

    tx = 560
    f_title = _fitted(d, label, SERIF_B, 46, W - tx - 90)
    d.text((tx, 146), label, font=f_title, fill=INK)
    tracked((tx, 146 + f_title.size + 10), quant, ImageFont.truetype(MONO, 13), MUTED, 1.0)
    tracked((tx, 146 + f_title.size + 32), f"{gib(str(path)):.2f} GiB ON DISK", ImageFont.truetype(MONO, 13), MUTED, 1.0)

    tracked((tx, 262), f"{st['score'] * 100:.1f}", ImageFont.truetype(SERIF_B, 96), TEAL, 1.0)
    tracked((tx + 4, 372), "% SCORE", ImageFont.truetype(MONO, 12), MUTED, 2.2)
    tracked((tx + 250, 268), f"{st['solved']}/12", ImageFont.truetype(SERIF_B, 54), INK, 1.0)
    tracked((tx + 254, 330), "TASKS FULLY SOLVED", ImageFont.truetype(MONO, 11), MUTED, 1.2)
    tracked((tx + 250, 368), f"{st['tok_s']:.0f} TOK/S  ·  {st['tok_task']:,.0f} TOK/TASK",
            ImageFont.truetype(MONO, 12), MUTED, 0.8)

    top, rowh = 486, 23
    ax0, aw = 690, 520
    tracked((86, top - 26), "PER-TASK SCORE  —  FIRST ATTEMPT PLUS ONE REPAIR", ImageFont.truetype(MONO, 11), MUTED, 1.2)
    d.line([(86, top - 8), (W - 86, top - 8)], fill=RULE + (255,), width=1)
    for i, (key, name) in enumerate(TASKS):
        y = top + i * rowh
        v = st["task"].get(key, 0.0)
        tracked((86, y + 2), f"{key}  {name}", ImageFont.truetype(MONO, 12),
                INK if i % 2 == 0 else MUTED, 0.6)
        d.rectangle((ax0, y + 3, ax0 + aw, y + 14), outline=RULE + (200,), width=1)
        d.rectangle((ax0, y + 3, ax0 + max(1, aw * v), y + 14), fill=TEAL + (205,))
        tracked((ax0 + aw + 12, y + 2), f"{v * 100:.0f}", ImageFont.truetype(MONO_B, 12), TEAL, 0.6)

    y = top + 12 * rowh + 10
    d.line([(86, y), (W - 86, y)], fill=INK + (170,), width=1)
    size = 27
    while d.textlength(verdict, ImageFont.truetype(SERIF, size)) > W - 200 and size > 16:
        size -= 1
    d.text((86, y + 10), verdict, font=ImageFont.truetype(SERIF, size), fill=INK)
    tracked((86, y + 50), "MEASURED, NOT QUOTED  ·  MODELBENCH CORE-V2  ·  19-20 OCT 2026",
            ImageFont.truetype(MONO, 11), MUTED, 1.4)

    _title_block(d, "FN-" + slug.upper()[:10])
    img.save(out)
    return out


if __name__ == "__main__":
    slug, out, kicker, verdict = sys.argv[1:5]
    print(render(out, slug, kicker, verdict))
