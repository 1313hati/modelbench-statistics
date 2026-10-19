#!/usr/bin/env python3
"""Aggregate the panel: score, solved tasks, tokens, rate, and the tasks nobody solves."""

from __future__ import annotations

import json
import statistics
from pathlib import Path

RUNS = Path("/home/hati/.hermes/cache/scratch/smallbench/runs")

ORDER = ["qwen3-14b", "qwen25-14b", "gemma3-12b", "qwen3-8b", "llama31-8b",
         "qwen25coder-7b", "deepseek-r1-7b", "mistral-7b", "qwen3-4b", "gemma3-4b"]


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
    solved = sum(1 for v in task_mean.values() if v >= 0.999)
    return {
        "slug": slug,
        "score": score,
        "solved": solved,
        "tasks": len(task_mean),
        "tok_s": statistics.median(rates) if rates else 0.0,
        "tok_per_task": toks / max(1, len(recs)),
        "task_mean": task_mean,
        "runs": len(recs) // max(1, len(task_mean)),
    }


def main() -> None:
    rows = []
    for slug in ORDER:
        s = summarise(slug)
        if s:
            rows.append(s)
    print(f"{'model':18} {'score':>6} {'solved':>7} {'tok/s':>6} {'tok/task':>9} {'runs':>5}")
    for s in rows:
        print(f"{s['slug']:18} {s['score']*100:5.1f}% {s['solved']:3}/{s['tasks']:<3} "
              f"{s['tok_s']:6.1f} {s['tok_per_task']:9,.0f} {s['runs']:5}")

    all_tasks = sorted({t for s in rows for t in s["task_mean"]})
    print("\nper task (mean of samples):")
    print(f"{'task':26}" + "".join(f"{s['slug'][:11]:>12}" for s in rows))
    for t in all_tasks:
        line = f"{t:26}"
        for s in rows:
            v = s["task_mean"].get(t)
            line += f"{v*100:11.0f} " if v is not None else f"{'-':>12}"
        print(line)

    shared = [t for t in all_tasks if all(s["task_mean"].get(t, 1) < 0.5 for s in rows)]
    print("\nfailed by every model:", ", ".join(shared) or "none")

    solvers = {t: [s["slug"] for s in rows if s["task_mean"].get(t, 0) >= 0.999] for t in all_tasks}
    print("\nsolved by few:", {t: v for t, v in solvers.items() if len(v) <= 2})


if __name__ == "__main__":
    main()
