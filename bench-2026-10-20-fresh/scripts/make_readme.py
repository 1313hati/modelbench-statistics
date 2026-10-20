#!/usr/bin/env python3
"""Rebuild this directory's README tables from results/summary.csv and tasks.csv."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
PLATES = ROOT / "plates"

LABEL = {
    "lfm25-8b-a1b": "LFM2.5-8B-A1B",
    "lfm25-2.6b": "LFM2.5-2.6B",
    "lfm25-1.2b": "LFM2.5-1.2B-Instruct",
    "lfm25-24b-a2b": "LFM2.5-24B-A2B",
    "bonsai2-9b": "Ternary-Bonsai-2-9B",
    "bonsai2-4b": "Ternary-Bonsai-2-4B",
}
VENDOR = {
    "lfm25-8b-a1b": "Liquid AI", "lfm25-2.6b": "Liquid AI",
    "lfm25-1.2b": "Liquid AI", "lfm25-24b-a2b": "Liquid AI",
    "bonsai2-9b": "Prism ML", "bonsai2-4b": "Prism ML",
}
QUANT = {"lfm25-8b-a1b": "Q8_0", "lfm25-2.6b": "Q8_0", "lfm25-1.2b": "Q8_0",
         "lfm25-24b-a2b": "Q4_K_M", "bonsai2-9b": "Q2_0", "bonsai2-4b": "Q2_0"}
GIB = {"lfm25-8b-a1b": "9.01", "lfm25-2.6b": "2.87", "lfm25-1.2b": "1.25",
       "lfm25-24b-a2b": "14.53", "bonsai2-9b": "2.56", "bonsai2-4b": "1.21"}
PLACE = {"lfm25-24b-a2b": "both cards", "default": "one card"}
ORDER = ["lfm25-24b-a2b", "bonsai2-9b", "bonsai2-4b", "lfm25-2.6b", "lfm25-8b-a1b", "lfm25-1.2b"]
FINDINGS = """## What the numbers say

- **The 24B MoE is the only model here that is a real coder.** 72.0% and six
  fully solved tasks, ahead of everything else by 26 points. It also needs
  14.5 GiB, so it is a two-card model, not a 12 GB one.
- **Dense beats sparse at this size.** LFM2.5-2.6B (44.8%) outscores
  LFM2.5-8B-A1B (34.5%) despite a third of the weights. The 8B MoE's 1B active
  path buys throughput (144 vs 95 tok/s), not accuracy.
- **Ternary is the value story.** Ternary-Bonsai-2-4B scores 45.8% on 1.21 GiB
  of weights — the whole model fits in less space than LFM2.5-1.2B at Q8_0
  (1.25 GiB), which scores 12.0%.
- **The 9B ternary is the same model with more room to think.** 46.2% and one
  extra solved task over the 4B, at half the speed and twice the disk.
- **Two tasks beat all six:** the JSON parser and the varint protocol were not
  fully solved by any model in this wave. The JSON parser is a context problem
  more than a knowledge problem: four of six ran the 16,384-token window out on
  it at least once, and LFM2.5-2.6B and the 24B burned the full window twice.
- **Speed is inversely related to care.** The 1.2B answers at 221 tok/s and
  solves nothing; the 24B answers at 118 tok/s and solves six tasks.
"""



def main() -> None:
    rows = {r["model"]: r for r in csv.DictReader((RESULTS / "summary.csv").open())}
    tasks = list(csv.DictReader((RESULTS / "tasks.csv").open()))
    order = [m for m in ORDER if m in rows] + [m for m in rows if m not in ORDER]

    out = ["# Fresh releases, October 2026", "",
           "Six models new to Hugging Face in the first half of October, run through",
           "`core-v2` on the same two-card rig as the [twelve-gigabyte panel](../bench-2026-10-19-12gb/).",
           "Five of six load entirely on one 12 GB card; the 24B MoE is split across both.",
           "", "| model | vendor | quant | weights | placement | score | solved | tok/s | tok/task |",
           "|---|---|---:|---:|---|---:|---:|---:|---:|"]
    for m in order:
        r = rows[m]
        out.append(f"| [{LABEL[m]}](plates/) | {VENDOR[m]} | {QUANT[m]} | {GIB[m]} GiB | "
                   f"{PLACE.get(m, PLACE['default'])} | {r['score_pct']}% | {r['solved']}/{r['tasks']} | "
                   f"{r['tok_per_s']} | {int(r['tok_per_task']):,} |")

    out += ["", FINDINGS, "![fresh releases](plates/00-panel.png)", "",
            "## Per task", "",
            "Share of each task's checks passed, first attempt plus one repair pass.", ""]
    head = "| task | " + " | ".join(LABEL[m] for m in order) + " |"
    out += [head, "|---|" + "---:|" * len(order)]
    for t in tasks:
        name = t["task"].replace("_", " ")
        cells = [t.get(m, "") for m in order]
        out.append(f"| {name} | " + " | ".join(cells) + " |")

    out += ["", "## Method", "",
            "See [method.md](method.md). Every run is one sample, `core-v2`, temperature 1.0,",
            "top_p 0.95, seed 42, 16,384 context, generation capped at 8,192 tokens per attempt.",
            "Reproduce the tables with `python3 scripts/analyze_fresh.py` and",
            "`python3 scripts/make_readme.py`.", ""]

    (ROOT / "README.md").write_text("\n".join(out))
    print(f"wrote {ROOT / 'README.md'} ({len(order)} models, {len(tasks)} tasks)")


if __name__ == "__main__":
    main()
