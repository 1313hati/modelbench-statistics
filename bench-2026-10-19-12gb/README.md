# bench-2026-10-19-12gb

Eight popular models, each loaded completely on one 12 GB card at 16,384 context, at the
largest quantization that fits entirely on the card. Two GPUs, one model each, same suite,
same harness.

| model | params (B) | quant | score | solved | completion tok/task | status |
|---|---|---|---|---|---|---|
| Qwen3-14B | 14.8 | Q4_K_M | 76.0% | 6/12 | 9,146 | complete |
| Qwen3-8B | 8.2 | Q8_0 | 52.9% | 3/12 | 8,496 | complete |
| Qwen3-4B-Instruct-2507 | 4.0 | Q4_K_M | 46.9% | 2/12 | 733 | complete |
| Qwen2.5-Coder-7B-Instruct | 7.6 | Q8_0 | 41.5% | 1/12 | 385 | complete |
| Gemma-3-12B-IT | 12.2 | Q5_K_M | 36.7% | 1/12 | 630 | complete |
| Gemma-3-4B-IT | 4.3 | Q4_K_M | 36.7% | 1/12 | 542 | complete |
| Qwen2.5-14B-Instruct | 14.7 | Q4_K_M | 36.6% | 1/12 | 502 | complete |
| Llama-3.1-8B-Instruct | 8.0 | Q8_0 | 32.4% | 1/12 | 445 | complete |
| DeepSeek-R1-Distill-Qwen-7B | 7.6 | Q8_0 | 31.8% | 2/12 | 9,584 | complete |
| Mistral-7B-Instruct-v0.3 | 7.2 | Q8_0 | 10.6% | 0/12 | 551 | complete |
| Qwen3.8-27B (reference, 24 GB card) | 27.0 | UD-Q4_K_XL | 100.0% | 1/12 | 4,157 | partial (1/12) |

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

- 14B class, 76.0 vs 36.6 — https://x.com/1313hati/status/2112271194661814347
- Gemma class, 36.7 vs 36.7 — https://x.com/1313hati/status/2112271936080564621
- 8B class, 52.9 vs 32.4 — https://x.com/1313hati/status/2112267358588833980
- 7B class, 41.4 vs 10.6 — https://x.com/1313hati/status/2112269302006968640
- Eight-model panel — https://x.com/1313hati/status/2112289303841677560
- Article: What fits in twelve gigabytes — https://x.com/1313hati/article/2112290740881514730

## Files

```
summary.csv / summary.json   one row per model
tasks.csv                    per-task score matrix
results/<slug>/results.jsonl raw records, one object per task
logs/                        harness + llama-server logs, progress.log
plates/                      published sheets
scripts/                     harness and plate generators for this run
```
