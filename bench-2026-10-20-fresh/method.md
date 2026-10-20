# Fresh releases, October 2026

Six models released in the two weeks before this bench, measured the same way as
the twelve-gigabyte panel: `core-v2`, twelve tasks, two phases per task (a first
attempt and one repair pass), greedy-free sampling at temperature 1.0, top_p
0.95, seed 42, one sample. Every request ran through llama.cpp's OpenAI server
with `--jinja`, 16,384 tokens of context, `-ngl all`, flash attention on,
q8_0 KV cache, and generation capped at 8,192 tokens.

## What is on the bench

| slug | model | quant | weights | placement |
|---|---|---|---:|---|
| `lfm25-8b-a1b` | LFM2.5-8B-A1B (Liquid AI, MoE, 8.3B total / 1B active) | Q8_0 | 9.01 GB | one RTX 3060, 12 GB |
| `lfm25-2.6b` | LFM2.5-2.6B (Liquid AI) | Q8_0 | 2.87 GB | one RTX 3060, 12 GB |
| `lfm25-1.2b` | LFM2.5-1.2B-Instruct (Liquid AI) | Q8_0 | 1.25 GB | one RTX 3060, 12 GB |
| `lfm25-24b-a2b` | LFM2.5-24B-A2B (Liquid AI, MoE, 23.9B total / 2B active) | Q4_K_M | 14.5 GB | **both** 3060s, tensor split |
| `bonsai2-9b` | Ternary-Bonsai-2-9B (Prism ML, ternary) | Q2_0 | 2.56 GB | one RTX 3060, 12 GB |
| `bonsai2-4b` | Ternary-Bonsai-2-4B (Prism ML, ternary) | Q2_0 | 1.21 GB | one RTX 3060, 12 GB |

Five of six load entirely on one 12 GB card with no CPU offload. The 24B MoE
cannot: at Q4_K_M it is 14.5 GB, so it is the one row measured across both cards
(`-sm layer -ts 0.5,0.5` over CUDA0+CUDA1; `-sm row` is rejected by the CUDA
backend on this build). It is included because it is the point of a 2x 3060
machine — the largest of this release that the pair can hold.

Quantization policy is unchanged from the 12 GB panel: the largest quantization
that leaves room for 16K of KV cache on the target placement. For LFM2.5's small
models that is Q8_0. For the ternary Bonsai models the only format mainline
llama.cpp reads is `Q2_0`; Prism's own `PQ2_0` / `PTQ1_0` packs need their fork
and were not used.

## Runs

Two models at a time, one per card, ports 8080 and 8081, in four waves:

1. `lfm25-8b-a1b` + `lfm25-2.6b`
2. `lfm25-1.2b` + `bonsai2-9b`
3. `bonsai2-4b` alone
4. `lfm25-24b-a2b` across both cards

Raw records: `../results/<slug>/results.jsonl` (copied from
`~/.hermes/cache/scratch/freshbench/runs`). `scripts/analyze_fresh.py` rebuilds
`results/summary.csv` and `results/tasks.csv` from those files;
`scripts/make_readme.py` rebuilds this directory's tables.

## Caveats

- One sample per task. Differences under roughly five points are inside the
  run-to-run spread this suite has shown on 4B-class models.
- Scores compare *what runs on this hardware*, not equal-precision quality.
- The 24B row is not directly comparable on speed: it holds a card pair, not a
  single card, and its KV cache lives across both devices.
- `bonsai2-*` are ternary-weight models; their per-token compute is still
  fp16/bf16 in llama.cpp's `Q2_0` path, so their speed is not a claim about
  ternary hardware.
