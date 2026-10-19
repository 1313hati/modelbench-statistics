#!/usr/bin/env python3
"""Rebuild summary.csv, summary.json, tasks.csv and README.md from the committed results.

Usage: python3 scripts/make_readme.py   (run from the run directory, e.g. bench-2026-10-19-12gb)
"""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

META = {
    "qwen3-14b": ("Qwen3-14B", 14.8, "Q4_K_M"),
    "qwen25-14b": ("Qwen2.5-14B-Instruct", 14.7, "Q4_K_M"),
    "gemma3-12b": ("Gemma-3-12B-IT", 12.2, "Q5_K_M"),
    "qwen3-8b": ("Qwen3-8B", 8.2, "Q8_0"),
    "llama31-8b": ("Llama-3.1-8B-Instruct", 8.0, "Q8_0"),
    "qwen25coder-7b": ("Qwen2.5-Coder-7B-Instruct", 7.6, "Q8_0"),
    "mistral-7b": ("Mistral-7B-Instruct-v0.3", 7.2, "Q8_0"),
    "deepseek-r1-7b": ("DeepSeek-R1-Distill-Qwen-7B", 7.6, "Q8_0"),
    "qwen3-4b": ("Qwen3-4B-Instruct-2507", 4.0, "Q4_K_M"),
    "gemma3-4b": ("Gemma-3-4B-IT", 4.3, "Q4_K_M"),
    "qwen38-27b": ("Qwen3.8-27B (reference, 24 GB card)", 27.0, "UD-Q4_K_XL"),
}

POSTS = [
    ("14B class, 76.0 vs 36.6", "https://x.com/1313hati/status/2112271194661814347"),
    ("Gemma class, 36.7 vs 36.7", "https://x.com/1313hati/status/2112271936080564621"),
    ("8B class, 52.9 vs 32.4", "https://x.com/1313hati/status/2112267358588833980"),
    ("7B class, 41.4 vs 10.6", "https://x.com/1313hati/status/2112269302006968640"),
    ("Eight-model panel", "https://x.com/1313hati/status/2112289303841677560"),
    ("Article: What fits in twelve gigabytes", "https://x.com/1313hati/article/2112290740881514730"),
]


def collect() -> list[dict]:
    rows = []
    for slug, (label, params, quant) in META.items():
        path = RESULTS / slug / "results.jsonl"
        if not path.exists():
            continue
        recs = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
        if not recs:
            continue
        per_task: dict[str, list[float]] = {}
        for r in recs:
            per_task.setdefault(r["task"], []).append(r["final_score"])
        means = {t: statistics.mean(v) for t, v in per_task.items()}
        rows.append({
            "slug": slug, "model": label, "params_b": params, "quant": quant,
            "tasks": len(means), "samples": len(recs),
            "score_pct": round(statistics.mean(means.values()) * 100, 2),
            "solved": sum(1 for v in means.values() if v >= 0.999),
            "completion_tokens_per_task": round(
                sum((r.get("first") or {}).get("completion_tokens") or 0 for r in recs) / len(recs)),
            "status": "complete" if len(means) == 12 else f"partial ({len(means)}/12)",
        })
    rows.sort(key=lambda r: (r["status"] != "complete", -r["score_pct"]))
    return rows


def matrix(rows: list[dict]) -> dict[str, dict[str, float]]:
    out = {}
    for r in rows:
        recs = [json.loads(x) for x in (RESULTS / r["slug"] / "results.jsonl").read_text().splitlines() if x.strip()]
        per: dict[str, list[float]] = {}
        for x in recs:
            per.setdefault(x["task"], []).append(x["final_score"])
        out[r["slug"]] = {t: statistics.mean(v) for t, v in per.items()}
    return out


def main() -> None:
    rows = collect()
    with open(ROOT / "summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (ROOT / "summary.json").write_text(json.dumps(
        {"suite": "modelbench-v1 (12 tasks, 2 phases)", "models": rows}, indent=2))

    mat = matrix(rows)
    tasks = sorted({t for m in mat.values() for t in m})
    with open(ROOT / "tasks.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["task"] + list(mat))
        for t in tasks:
            w.writerow([t] + [f"{mat[s].get(t, '')}" for s in mat])

    table = "\n".join(
        ["| model | params (B) | quant | score | solved | completion tok/task | status |", "|---|---|---|---|---|---|---|"]
        + [f"| {r['model']} | {r['params_b']:.1f} | {r['quant']} | {r['score_pct']:.1f}% | "
           f"{r['solved']}/12 | {r['completion_tokens_per_task']:,} | {r['status']} |" for r in rows])

    posts = "\n".join(f"- {name} — {url}" for name, url in POSTS)
    readme = f"""# bench-2026-10-19-12gb

Eight popular models, each loaded completely on one 12 GB card at 16,384 context, at the
largest quantization that fits entirely on the card. Two GPUs, one model each, same suite,
same harness.

{table}

Score is the mean of the twelve per-task final scores (public + hidden checks, first
attempt plus one repair pass). *solved* counts tasks that reached 100%. Completion tokens
are first-phase only, so a capped-then-retried attempt does not inflate the figure.

## Method

- Suite: ModelBench v1, 12 tasks, 296 checks — parsing, SQL, async, concurrency, review,
  bit-level protocol, feature work.
- Harness: `llama.cpp` `llama-server`, `--jinja`, `-ngl all`, `-fa on`, KV cache q8_0,
  16,384 context, one slot, `-n 8192` generation cap with one larger-cap retry on truncation.
- Quantization: Q8_0 where it fits, else the largest Q4/Q5 that fits — this is a
  what-actually-runs comparison, not a same-precision one.
- Hardware: 2 × RTX 3060 12 GB, no CPU offload.

## Read-outs

- Qwen3-14B wins at 76.0% with 9,146 completion tokens per task — 18× Qwen2.5-14B's 502
  for a 39-point gap. Same parameter count; the difference is deliberation, not capacity.
- Gemma-3-12B and Gemma-3-4B both score 36.7%: one task solved each, the same five tasks at
  zero, 630 vs 542 tokens. Doubling parameters bought 16% more tokens and nothing else.
- At 7B, post-training beats size: Qwen2.5-Coder 41.4% against Mistral-7B v0.3 10.6%.
- R1-Distill-Qwen-7B spends 9,584 tokens per task to reach 31.8% and solves two — more
  tokens than Qwen3-14B and less than half its score. Reasoning traces are not free score.
- The 8B rung favours thinking: Qwen3-8B 52.9% vs Llama-3.1-8B 32.4%.

## Posts

{posts}

## Files

```
summary.csv / summary.json   one row per model
tasks.csv                    per-task score matrix
results/<slug>/results.jsonl raw records, one object per task
logs/                        harness + llama-server logs, progress.log
plates/                      published sheets
scripts/                     harness and plate generators for this run
```
"""
    (ROOT / "README.md").write_text(readme)
    print(f"wrote {len(rows)} rows")


if __name__ == "__main__":
    main()
