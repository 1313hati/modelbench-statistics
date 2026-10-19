# What fits in twelve gigabytes: eight models, one card

Every model in this test had to load completely on a single RTX 3060 — 12 GB of VRAM, no
CPU offload, 16,384 tokens of context, the largest quantization that fits entirely on the
card. Not the largest that half-fits. Not the one that spills a few layers into system RAM
and then crawls. If it did not fit, it did not run.

That constraint decides more than most benchmarks admit. A 14B model at Q4_K_M fits; the
same model at Q8 does not. An 8B at Q8_0 fits with room for KV cache; the 12B Gemma needs
Q5_K_M to leave space for 16K of context. The panel is therefore not a same-precision
comparison — it is a what-can-you-actually-run comparison, which is the only question a
person with one 12 GB card is asking.

## The suite

ModelBench v1: twelve tasks, 296 checks, each task run as a first attempt plus one repair
pass. The work is the kind that shows up in real repositories — weighted job scheduling,
text justification, a JSON parser, a SQL report, an async connection pool, a concurrency
bug fix, a CSV reader against RFC 4180, a bit-level varint protocol, and a feature built on
top of an existing ledger.

Scoring is per task: public checks plus hidden checks, so a solution that only satisfies
the visible cases does not score. Generation is capped at 8,192 tokens; a truncated answer
is retried once with a larger cap, so long deliberations are not scored on a cut-off.

Two cards, one model each, same harness: llama.cpp's server, `--jinja`, full offload,
flash attention, q8_0 KV cache, one slot.

## The table

- Qwen3-14B, Q4_K_M — 76.0%, 6/12 solved, 9,146 completion tokens per task
- Qwen3-8B, Q8_0 — 52.9%, 3/12, 8,496
- Qwen2.5-Coder-7B, Q8_0 — 41.4%, 1/12, 385
- Gemma-3-12B, Q5_K_M — 36.7%, 1/12, 630
- Qwen2.5-14B, Q4_K_M — 36.6%, 1/12, 502
- Llama-3.1-8B, Q8_0 — 32.4%, 1/12, 445
- R1-Distill-Qwen-7B, Q8_0 — 31.8%, 2/12, 9,584
- Mistral-7B v0.3, Q8_0 — 10.6%, 0/12, 551

## What the numbers say

**Deliberation, not capacity, separates the 14B pair.** Qwen3-14B and Qwen2.5-14B carry the
same parameter count and land 39 points apart. The difference is 9,146 completion tokens
against 502 — eighteen times the generation for the same twelve problems. Qwen3 thinks
before it answers, and on this suite thinking is worth more than four times the model's
size advantage would suggest. It also means the 76.0% is expensive at the wall: on a 12 GB
card those tokens arrive at roughly 30 per second.

**Parameters alone bought nothing in the Gemma pair.** Gemma-3-12B scored 36.7%; Gemma-3-4B
scored 36.7%. One task solved each. The same five tasks at zero — JSON parser, async pool,
thread queue, varint protocol, ledger feature. The 12B spent 16% more completion tokens to
arrive at the same place. Whatever the extra eight billion parameters learned, this suite
does not ask for it.

**At 7B, post-training is most of the model.** Qwen2.5-Coder-7B reaches 41.4% while
Mistral-7B v0.3 reaches 10.6% — nearly four times the score for the same parameter budget,
and it does it in 385 tokens per task against Mistral's 551. A code-tuned 7B is a better
investment on this kind of work than a general 7B of identical size, and it is not close.

**Reasoning traces are not free score.** R1-Distill-Qwen-7B spends 9,584 completion tokens
per task — more than the winner — and reaches 31.8%. It solves two tasks outright, which
edges out several models that score higher on the mean, but its zero tasks are flat zeros:
the JSON parser, the thread queue, the varint protocol and the CSV reader all came back
unfinished after a capped retry. A 7B base doing long chain-of-thought produces a lot of
thinking and not much code.

**The 8B rung favours the thinker.** Qwen3-8B at 52.9% is 20 points clear of Llama-3.1-8B
at 32.4%, and it pays 8,496 tokens per task for the privilege. At this size the deliberation
budget is what separates the two, not the training data.

## How far these numbers go

Twelve tasks is a small instrument. One task is worth 8.3 percentage points, so a gap of a
few points is noise — Gemma-3-12B at 36.7 and Qwen2.5-14B at 36.6 are a tie, and so are
Gemma-3-12B and Qwen2.5-Coder-7B within one task. The ordering that survives that
resolution is: Qwen3-14B far ahead, Qwen3-8B next, the 36–41 cluster, then the 7B general
models at the bottom.

The quantization ladder is a real confound. Qwen3-14B ran at Q4_K_M and Qwen3-8B at Q8_0;
the 8B had more bits per weight. That is not a flaw in the test — it is the test. On a
12 GB card you cannot have both, and pretending otherwise produces numbers nobody can
reproduce at home.

## What to run

If latency is acceptable and the task is hard, Qwen3-14B at Q4_K_M is the strongest thing
that fits on one 12 GB card by a wide margin. If you want an answer this second, Qwen2.5-Coder-7B
gives you 41.4% at 385 tokens per task — twenty-four times fewer tokens than the winner for
just over half its score. Qwen3-8B is the middle: 52.9%, eight thousand tokens, and it fits with
Q8 weights.

Mistral-7B v0.3 at 10.6% and zero solved tasks is not worth a slot on this hardware for
this kind of work.

## Reproduce it

Every number here comes from a committed results file, not an estimate. The repository holds
the raw `results.jsonl` per model, the harness and server logs for each run, the plate
generators, and a `summary.csv` that is rebuilt from those files:

https://github.com/1313hati/modelbench-statistics

ModelBench itself, including the twelve tasks and their checks:

https://github.com/1313hati/modelbench
