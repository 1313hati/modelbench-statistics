# modelbench-statistics

Machine-measured results from [ModelBench](https://github.com/1313hati/modelbench) runs on local hardware.
Every number here comes from a committed `results.jsonl`; nothing is estimated.

## bench-2026-10-19-12gb — eight popular models on one 12 GB card

Each model loads completely on a single RTX 3060 (12 GB) at 16,384 context, at the
largest quantization that fits entirely on the card. Same suite, same seeds, two GPUs
running one model each in parallel.

| model | params (B) | quant | GGUF (GiB) | score | solved | completion tok/task |
|---|---|---|---|---|---|---|
| Qwen3-14B | 14.8 | Q4_K_M | 8.38 | 76.0% | 6/12 | 9,146 |
| Qwen3-8B | 8.2 | Q8_0 | 8.11 | 52.9% | 3/12 | 8,496 |
| Qwen3-4B-Instruct-2507 | 4.0 | Q4_K_M | — | 46.9% | 2/12 | 733 |
| Qwen2.5-Coder-7B-Instruct | 7.6 | Q8_0 | 7.54 | 41.5% | 1/12 | 385 |
| Gemma-3-12B-IT | 12.2 | Q5_K_M | 7.87 | 36.7% | 1/12 | 630 |
| Gemma-3-4B-IT | 4.3 | Q4_K_M | — | 36.7% | 1/12 | 542 |
| Qwen2.5-14B-Instruct | 14.7 | Q4_K_M | 8.37 | 36.6% | 1/12 | 502 |
| Llama-3.1-8B-Instruct | 8.0 | Q8_0 | 7.95 | 32.4% | 1/12 | 445 |
| Mistral-7B-Instruct-v0.3 | 7.2 | Q8_0 | 7.17 | 10.6% | 0/12 | 551 |
| DeepSeek-R1-Distill-Qwen-7B | 7.6 | Q8_0 | 7.54 | 100.0% | 1/12 | 5,981 |  _partial (1/12)_
| Qwen3.8-27B (reference, 24 GB card) | 27.0 | UD-Q4_K_XL | — | 100.0% | 1/12 | 4,157 |  _partial (1/12)_

Score is the mean of the twelve per-task final scores (visible checks + hidden checks,
each task run as a first attempt plus one repair pass). *solved* counts tasks that
reached 100%. Token counts are the first-phase completion tokens only.

### Method

- Suite: ModelBench v1 — 12 tasks (parsing, SQL, async, concurrency, review, protocol,
  feature work), each with public and hidden checks.
- Harness: `llama.cpp` `llama-server`, `--jinja`, `-ngl all`, `-fa on`, KV cache q8_0,
  16,384 context, one slot.
- Generation is capped at the suite-declared 8,192 tokens; a truncated attempt is
  retried once with a larger cap, so long deliberators (Qwen3, R1) are not scored on a
  cut-off answer.
- Quantization: Q8_0 where it fits, otherwise the largest Q4/Q5 that fits. The panel is
  therefore not a same-precision comparison — it is a *what-can-you-actually-run* comparison.
- Hardware: 2 × RTX 3060 12 GB, one model per card, no offload to CPU.

### Read-outs

- Qwen3-14B at 76.0% is bought with 9,146 completion tokens per task — 18× Qwen2.5-14B,
  which lands at 36.6% with 502 tokens. Same parameter count, 39-point gap.
- Gemma-3-12B scores 36.7%, exactly Gemma-3-4B's 36.7%: one task solved each, the same
  five tasks at zero. Doubling parameters moved nothing on this suite.
- Post-training beats size at 7B: Qwen2.5-Coder 41.4% vs Mistral-7B v0.3 10.6%.
- At 8B, thinking is worth 20.5 points (Qwen3-8B 52.9% vs Llama-3.1-8B 32.4%).

### Posts

- 14B class — https://x.com/1313hati/status/2112271194661814347
- Gemma class — https://x.com/1313hati/status/2112260281695195474
- 8B class — https://x.com/1313hati/status/2112267358588833980
- 7B class — https://x.com/1313hati/status/2112269302006968640

### Files

```
summary.csv / summary.json   one row per model, all derived numbers
tasks.csv                    per-task score matrix
results/<slug>/results.jsonl raw records, one JSON object per task
logs/<slug>.run.log          harness stdout per model
logs/<slug>.server.log       llama-server stdout per model (timings, slot stats)
logs/progress.log            wall-clock start/stop per model
plates/                      the published sheets
scripts/                     harness + plate generators used for this run
```

Partial rows: `deepseek-r1-7b` was still running when this snapshot was written, and
`qwen38-27b` is a reference run on a 24 GB card that was aborted after one task; both are
marked *partial* and excluded from the read-outs above.
