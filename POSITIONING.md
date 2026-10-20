# What this is

One question, asked over and over:

**What can a person with consumer hardware actually run, and what does it cost them in time?**

Not which model wins a leaderboard. Not which model is best at Q8 on a datacenter card.
The question is the one somebody with a 12 GB GPU is asking at eleven at night: will this
fit, at what quantization, how slow is it, and is it good enough for real work.

Everything in this repository is an attempt to answer that with evidence instead of vibes.

## The constraint is the instrument

Every model must load **completely** into VRAM at 16,384 tokens of context, at the largest
quantization that fits entirely — no CPU offload, no layers spilled into system RAM, no
"it works if you wait". If it does not fit, it does not run. When a model needs both cards,
the row says so and its speed is reported as pair-split, never mixed into one-card numbers.

This is deliberately not a same-precision comparison. A 14B at Q4_K_M fits and the same
model at Q8 does not; a 12B needs Q5_K_M to leave room for a 16K KV cache. That is not a
flaw in the test — it is the test. Pretending otherwise produces numbers nobody can
reproduce at home.

## The work looks like a repository

Twelve tasks, 296 checks: a weighted job scheduler, text justification, a JSON parser, a
SQL report, an async connection pool, a concurrency bug fix, a CSV reader against RFC 4180,
a bit-level varint protocol, and a feature built on an existing ledger. Each task is a
first attempt plus one repair pass, scored on public and hidden checks, so a solution that
only satisfies the visible cases does not score. Tokens are counted. Length stops are
recorded. A truncated answer is retried once with a larger ceiling rather than scored on a
cut-off.

## Every number has a file behind it

Per model: `results.jsonl` with one record per task, the harness and server logs, a
`summary.json`, and a `REPORT.md`. Per panel: `summary.csv` and `tasks.csv` rebuilt from
those records by a committed script. The plates are generated from the same data — each
ASCII die is that model's own tensor table, so the picture cannot drift from the numbers.

If a figure is not in `results.jsonl`, it does not go in a post.

## What the record says so far

Fourteen models across two panels, and the constraint keeps overturning the obvious answer:

- **Fitting changes the ranking.** A 14B at Q4_K_M beats every 8B at Q8 on score, and pays
  for it at roughly 30 tokens per second on a 12 GB card.
- **Deliberation is a variable as large as size.** Qwen3-14B and Qwen2.5-14B carry the same
  parameter count and land 39 points apart; the difference is 9,146 completion tokens per
  task against 502.
- **Parameters alone bought nothing.** Gemma-3-12B and Gemma-3-4B both scored 36.7% with one
  task solved each, failing the same five tasks.
- **At 7B, post-training is most of the model.** Qwen2.5-Coder-7B reaches 41.4% where
  Mistral-7B v0.3 reaches 10.6%, in fewer tokens per task.
- **Fresh releases, October 2026.** The 24B MoE is the only model in that wave that behaves
  like a real coder (72.0%, 6/12) and it needs both cards; the 4B ternary at 45.8% on
  1.21 GiB is the value story of the panel.
- **Two tasks beat everyone.** The JSON parser and the varint protocol were not fully solved
  by any model in either wave.

## The voice

These rules bind every X post, every README, every article, every commit message.

1. **The first line is a number or a constraint, never a preamble.** No "Excited to share",
   no "Let's dive in".
2. **A post answers four things:** what ran, on what hardware and quantization, at what
   cost in tokens or seconds, and what that changes. If one is missing, it is not ready.
3. **Quote the measurement, not the adjective.** "72.0%, 6/12, 118 tok/s, 14.5 GiB across
   two cards" does the work that "impressive" cannot.
4. **Name the ceiling exactly.** The generation cap is not the context window; the first
   attempt is not the repair pass; one card is not two. A number without its ceiling is a
   rumour.
5. **Declare the noise.** Twelve tasks means one task is 8.3 points. Ties are called ties,
   and a 0.1-point gap is not a ranking.
6. **No hype vocabulary.** No insane, beast, game-changer, blowout, destroys. No emoji, no
   hashtags, no rocket ships. Plain declaratives.
7. **Each post stands alone**, because most readers will see exactly one of them. The last
   post of a wave lists every row in a single block and carries the panel sheet.
8. **The plate is evidence.** Generated from the committed data, never decoration, never a
   stock image, never a number typed by hand into the drawing.
9. **A wrong number is deleted and reposted corrected**, under a new version slug, and the
   repository records the correction. Never quietly edited, never left standing.
10. **Limits get a paragraph, not a footnote.** Twelve tasks is a small instrument, one
    sample per model is one sample, and the quantization ladder is a confound by design.
    Saying so is part of the result, not an apology for it.

## For the repository

- Contract per panel: `README.md` (index and tables), `method.md` (exact server flags,
  quantization, context, placement), `results/<model>/` (raw records, summary, report,
  run metadata), `logs/`, `plates/`, `scripts/` (analysis, README generator, plate
  renderers), and `article.md` when a long-form piece exists.
- README tables are generated by script, never typed.
- Commit messages name the wave and the models, and say what was measured.
- Every long-form piece ends with how to reproduce it and what it does not prove.

## Three lines, for anywhere this needs introducing

I benchmark what actually runs on consumer GPUs: models that must fit entirely inside 12 GB
of VRAM at 16K context, measured on work that looks like a real repository, with every token
record committed to a public repository. Two cards, fourteen models so far, no estimates.
The point is not another leaderboard — it is an answer you can reproduce at home.
