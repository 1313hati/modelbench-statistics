#!/usr/bin/env python3
"""The fresh-releases sheet: six new models, one 12 GB card each.

A 3 x 2 field sheet in the same register as the twelve-gigabyte panel: paper,
drafting grid, one ASCII die per model read from its own GGUF tensor table.

    python3 fresh_panel.py out.png
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import blueprint as bp
from gguf_map import die_image, profile, to_ascii
from small_models_plate import (INK, MUTED, MONO, MONO_B, OXBLOOD, PAPER, PAPER_DEEP,
                                RULE, SERIF, SERIF_B, TEAL, _fitted, _tracked,
                                ascii_block, families, gib, paper, stats)


def _title_block(d, dwg: str) -> None:
    """Local title block: small_models_plate's one is pinned to its own canvas."""
    bw, bh = 330, 66
    x1, y1 = W - 40, H - 40
    x0, y0 = x1 - bw, y1 - bh
    d.rectangle((x0, y0, x1, y1), fill=PAPER + (245,))
    d.rectangle((x0, y0, x1, y1), outline=INK + (200,), width=2)
    d.line([(x0, y0 + 36), (x1, y0 + 36)], fill=INK + (140,), width=1)
    _tracked(d, (x0 + 10, y0 + 10), dwg.upper() + "  MODELBENCH",
             ImageFont.truetype(MONO_B, 15), INK, 1.4)
    _tracked(d, (x0 + 10, y0 + 44), "1:1  ·  20 OCT 2026",
             ImageFont.truetype(MONO, 12), MUTED, 1.0)
    _tracked(d, (x0 + 224, y0 + 44), "@1313hati",
             ImageFont.truetype(MONO, 12), OXBLOOD, 1.0)

W, H = 1600, 1300
MODELS_DIR = Path("/home/hati/.cache/llama-models")
RUNS = Path("/home/hati/.hermes/cache/scratch/freshbench/runs")

MODELS = [
    ("lfm25-8b-a1b", "LFM2.5-8B-A1B", "LFM2.5-8B-A1B-Q8_0.gguf", "Q8_0", "ONE CARD"),
    ("lfm25-2.6b", "LFM2.5-2.6B", "LFM2.5-2.6B-Q8_0.gguf", "Q8_0", "ONE CARD"),
    ("lfm25-1.2b", "LFM2.5-1.2B", "LFM2.5-1.2B-Instruct-Q8_0.gguf", "Q8_0", "ONE CARD"),
    ("lfm25-24b-a2b", "LFM2.5-24B-A2B", "LFM2.5-24B-A2B-Q4_K_M.gguf", "Q4_K_M", "TWO CARDS"),
    ("bonsai2-9b", "TERNARY-BONSAI-2-9B", "Ternary-Bonsai-2-9B-Q2_0.gguf", "Q2_0", "ONE CARD"),
    ("bonsai2-4b", "TERNARY-BONSAI-2-4B", "Ternary-Bonsai-2-4B-Q2_0.gguf", "Q2_0", "ONE CARD"),
]


def load(slug: str) -> dict | None:
    p = RUNS / slug / "results.jsonl"
    if not p.exists():
        return None
    recs = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
    if not recs:
        return None
    by_task: dict[str, list[float]] = {}
    toks = 0
    rates = []
    for r in recs:
        by_task.setdefault(r["task"], []).append(r["final_score"])
        for phase in ("first", "repair"):
            ph = r.get(phase) or {}
            toks += (ph.get("prompt_tokens") or 0) + (ph.get("completion_tokens") or 0)
            if ph.get("tok_per_s"):
                rates.append(ph["tok_per_s"])
    means = {t: statistics.mean(v) for t, v in by_task.items()}
    return {"score": statistics.mean(means.values()),
            "solved": sum(1 for v in means.values() if v >= 0.999),
            "tasks": len(means),
            "tok_s": statistics.median(rates) if rates else 0.0,
            "tok_task": toks / max(1, len(recs)),
            "complete": len(means) == 12}


def cell(d, x: int, y: int, slug: str, label: str, fname: str, quant: str, place: str) -> None:
    path = MODELS_DIR / fname
    st = load(slug)
    tracked = lambda xy, txt, f, c, tr: _tracked(d, xy, txt, f, c, tr)

    cols, size = 40, 8.0
    if path.exists():
        blocks, ts = profile(str(path))
        rows = to_ascii(die_image(families(blocks), 700, 700), cols=cols, gamma=0.85)
        ascii_block(d, cols, x, y, rows, size=size, colour=INK, alpha_max=235)
        n_blocks = len({int(t["name"].split(".")[1]) for t in ts
                        if t["name"].startswith("blk.") and len(t["name"].split(".")) > 2
                        and t["name"].split(".")[1].isdigit()})
        meta = f"{n_blocks} LAYERS  ·  {quant}  ·  {gib(str(path)):.2f} GiB  ·  {place}"
    else:
        meta = f"{quant}  ·  {place}"

    lx = x + cols * size * 0.6 + 26
    tracked((lx, y + 2), label, ImageFont.truetype(MONO_B, 17), INK, 1.0)
    tracked((lx, y + 30), meta, ImageFont.truetype(MONO, 11), MUTED, 0.6)

    if st and st["complete"]:
        tracked((lx, y + 58), f"{st['score'] * 100:.1f}", ImageFont.truetype(SERIF_B, 60), TEAL, 1.0)
        tracked((lx + 2, y + 136), "% SCORE", ImageFont.truetype(MONO, 10), MUTED, 2.0)
        tracked((lx, y + 168), f"SOLVED {st['solved']}/12", ImageFont.truetype(MONO_B, 14), INK, 1.2)
        tracked((lx, y + 194), f"{st['tok_s']:.0f} TOK/S  ·  {st['tok_task']:,.0f} TOK/TASK",
                ImageFont.truetype(MONO, 11), MUTED, 0.6)
    else:
        done = st["tasks"] if st else 0
        tracked((lx, y + 70), f"RUNNING {done}/12", ImageFont.truetype(MONO_B, 16), MUTED, 1.2)


def render(out: str) -> str:
    img = paper(W, H)
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(40, W - 40, 24):
        d.line([(x, 40), (x, H - 40)], fill=INK + (12 if (x - 40) % 120 == 0 else 6,), width=1)
    for y in range(40, H - 40, 24):
        d.line([(40, y), (W - 40, y)], fill=INK + (12 if (y - 40) % 120 == 0 else 6,), width=1)
    d.rectangle((40, 40, W - 40, H - 40), outline=INK + (210,), width=2)
    d.rectangle((50, 50, W - 50, H - 50), outline=INK + (90,), width=1)

    tracked = lambda xy, txt, f, c, tr: _tracked(d, xy, txt, f, c, tr)
    tracked((86, 70), "FIELD NOTE  ·  FRESH RELEASES  ·  MEASURED", ImageFont.truetype(MONO, 18), OXBLOOD, 2.6)
    head = "Six models released this month, measured"
    f_head = _fitted(d, head, SERIF_B, 64, W - 2 * 88)
    d.text((86, 94), head, font=f_head, fill=INK)
    tracked((88, 94 + f_head.size + 12),
            "LFM2.5 (LIQUID AI)  ·  TERNARY BONSAI 2 (PRISM ML)  ·  CORE-V2: 12 TASKS, 296 CHECKS  ·  LLAMA.CPP, 16,384 CTX",
            ImageFont.truetype(MONO, 14), MUTED, 1.2)
    d.line([(86, 218), (W - 86, 218)], fill=RULE + (255,), width=2)

    for i, (slug, label, fname, quant, place) in enumerate(MODELS):
        col, row = i % 2, i // 2
        cell(d, 86 + col * 750, 250 + row * 292, slug, label, fname, quant, place)

    d.line([(86, 1140), (W - 86, 1140)], fill=RULE + (255,), width=1)
    note = ImageFont.truetype(MONO, 13)
    tracked((86, 1152), "EACH DIE IS THAT MODEL'S OWN TENSOR TABLE: ROWS ARE ROLES, COLUMNS ARE BLOCKS, DARKNESS IS SIZE ON DISK.",
            note, MUTED, 0.8)
    tracked((86, 1174), "24B MoE IS SPLIT ACROSS BOTH CARDS; EVERY OTHER ROW LOADED ENTIRELY ON ONE 12 GB CARD WITH NO CPU OFFLOAD.",
            note, MUTED, 0.8)
    _title_block(d, "FN-005")
    img.save(out)
    return out


if __name__ == "__main__":
    print(render(sys.argv[1] if len(sys.argv) > 1
                 else "/home/hati/.hermes/cache/scratch/fresh-panel.png"))
