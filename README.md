# modelbench-statistics

Raw results and logs from [ModelBench](https://github.com/1313hati/modelbench) runs on local
hardware. Every number is derived from a committed `results.jsonl` — no estimates.

| run | what it covers |
|---|---|
| [bench-2026-10-19-12gb](bench-2026-10-19-12gb/) | Eight popular models, each fully on one 12 GB card at 16K context, largest quant that fits |
| [bench-2026-10-20-fresh](bench-2026-10-20-fresh/) | Six October releases — LFM2.5 (1.2B to 24B-A2B) and Prism ML's ternary Bonsai 2 — five on one 12 GB card, the 24B MoE across both |

Each run directory holds its method notes, `summary.csv`, the per-task matrix, the raw
`results.jsonl` per model, the harness and server logs, the published plates, and the
generator scripts used to produce them.

## Reading the numbers

- **score** — mean of the twelve per-task final scores. Each task is a first attempt plus
  one repair pass, scored on public and hidden checks.
- **solved** — tasks that reached 100%.
- **completion tok/task** — first-phase completion tokens only, so a heavy deliberator's
  second attempt does not inflate the figure.
- Comparisons are same-quant only where the fit allows; a 14B in Q4 and an 8B in Q8 are
  not equal precision, and the tables say so.
