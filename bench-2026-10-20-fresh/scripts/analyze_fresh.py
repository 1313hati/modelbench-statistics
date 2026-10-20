#!/usr/bin/env python3
"""Aggregate the fresh-releases bench: score, solved tasks, tokens, rate."""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

RUNS = Path("/home/hati/.hermes/cache/scratch/freshbench/runs")
OUT = Path(__file__).resolve().parent.parent / "results"

ORDER = ["lfm25-8b-a1b", "lfm25-2.6b", "lfm25-1.2b", "lfm25-24b-a2b",
         "bonsai2-9b", "bonsai2-4b"]


def load(slug: str):
    p = RUNS / slug / "results.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def summarise(slug: str):
    recs = load(slug)
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
    task_mean = {t: statistics.mean(v) for t, v in by_task.items()}
    score = statistics.mean(task_mean.values())
    return {
        "slug": slug,
        "score": score,
        "solved": sum(1 for v in task_mean.values() if v >= 0.999),
        "tasks": len(task_mean),
        "tok_s": statistics.median(rates) if rates else 0.0,
        "tok_per_task": toks / max(1, len(recs)),
        "task_mean": task_mean,
        "runs": len(recs) // max(1, len(task_mean)),
    }


def main() -> None:
    rows = [s for s in (summarise(slug) for slug in ORDER) if s]
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "score_pct", "solved", "tasks", "tok_per_s", "tok_per_task"])
        for s in rows:
            w.writerow([s["slug"], f"{s['score']*100:.1f}", s["solved"], s["tasks"],
                        f"{s['tok_s']:.1f}", f"{s['tok_per_task']:.0f}"])
    all_tasks = sorted({t for s in rows for t in s["task_mean"]})
    with (OUT / "tasks.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["task"] + [s["slug"] for s in rows])
        for t in all_tasks:
            w.writerow([t] + [f"{s['task_mean'][t]*100:.0f}" if t in s["task_mean"] else ""
                              for s in rows])

    print(f"{'model':18} {'score':>6} {'solved':>7} {'tok/s':>6} {'tok/task':>9}")
    for s in rows:
        print(f"{s['slug']:18} {s['score']*100:5.1f}% {s['solved']:3}/{s['tasks']:<3} "
              f"{s['tok_s']:6.1f} {s['tok_per_task']:9,.0f}")

    print("\nper task (%):")
    print(f"{'task':26}" + "".join(f"{s['slug'][:12]:>13}" for s in rows))
    for t in all_tasks:
        line = f"{t:26}"
        for s in rows:
            v = s["task_mean"].get(t)
            line += f"{v*100:12.0f} " if v is not None else f"{'-':>13}"
        print(line)

    dead = [t for t in all_tasks if all(s["task_mean"].get(t, 1) < 0.5 for s in rows)]
    print("\nfailed by every model:", ", ".join(dead) or "none")
    if rows:
        best = max(rows, key=lambda s: s["score"])
        print("leader:", best["slug"], f"{best['score']*100:.1f}%")


if __name__ == "__main__":
    main()
