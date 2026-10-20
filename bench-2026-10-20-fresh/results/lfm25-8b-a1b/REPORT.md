# modelbench — lfm25-8b-a1b on core-v2

Single run on suite `core-v2`: **33.5%** mean first-attempt task score, 16.7% of attempts fully solved before feedback.

_Generated 2026-10-20T00:23:30 by modelbench 2.1.0. Suite: `core-v2`. _

## Headline

Scores are means over tasks (each task weighs the same), then over samples. `first` is the answer before any feedback; `final` allows one repair turn in which only failing assertion messages are returned.

| metric | adhoc |
|---|---|
| records / expected | 12 / 12 |
| samples / task | 1 |
| mean task score, first | 33.5% |
| 95% CI, first · final | 11.3–57.7% · 13.0–58.3% |
| mean task score, final | 34.5% |
| first-attempt assertions | 84/194 (43.3%) |
| fully solved, first | 16.7% |
| fully solved, final | 16.7% |
| repair turns / improved / solved | 10 / 1 / 0 |
| median call wall | 43.1s |
| p90 call wall | 114.0s |
| median output tokens / call | 6178 |
| prompt tokens, total | 29,300 |
| completion tokens, total | 233,046 |
| tokens per solved task | 116523 |
| wall clock, total | 34.4 min |
| median decode speed | 143.8 tok/s |
| median TTFT | 0.13s |
| answers cut by token cap | 2 |

## Per task

| task | category | adhoc | best |
|---|---|---|---|
| t01_weighted_jobs | algorithms | 100.0% | adhoc |
| t02_text_justify | spec | 0.0% | adhoc |
| t03_json_parser | parsing | 0.0% | adhoc |
| t04_sql_report | sql | 85.7% | adhoc |
| t05_async_pool | async | 16.7% | adhoc |
| t06_repo_bugfix | repo | 64.0% | adhoc |
| t07_thread_queue | concurrency | 0.0% | adhoc |
| t08_code_review | review | 35.7% | adhoc |
| t09_csv_rfc4180 | parsing | 0.0% | adhoc |
| t10_pairs_refactor | refactor | 100.0% | adhoc |
| t11_varint_protocol | binary | 0.0% | adhoc |
| t12_ledger_feature | longcontext | 0.0% | adhoc |

## Per category

| category | adhoc |
|---|---|
| algorithms | 100.0% |
| async | 16.7% |
| binary | 0.0% |
| concurrency | 0.0% |
| longcontext | 0.0% |
| parsing | 0.0% |
| refactor | 100.0% |
| repo | 64.0% |
| review | 35.7% |
| spec | 0.0% |
| sql | 85.7% |

## Where it fails

Failing assertions from the first attempt, counted once per record and grouped by assertion name. A name that fails in both samples of a task is a systematic gap, not noise.

| assertion | adhoc |
|---|---|
| `28 nights discount` | 1 record, 1 task |
| `28 nights total` | 1 record, 1 task |
| `back-to-back after is allowed` | 1 record, 1 task |
| `back-to-back before is allowed` | 1 record, 1 task |
| `basic` | 1 record, 1 task |
| `calls fn with item and index` | 1 record, 1 task |
| `does not mutate items` | 1 record, 1 task |
| `empty resolves [] without calls` | 1 record, 1 task |
| `exhausted retries rejects with last error` | 1 record, 1 task |
| `fail-fast stops starting new items` | 1 record, 1 task |
| `false-positive pricing.py` | 1 record, 1 task |
| `half-up discount and tax` | 1 record, 1 task |

## Provenance

| run | endpoint | served id | samples | records | suite | digest |
|---|---|---|---|---|---|---|
| adhoc | http://127.0.0.1:8080/v1 | lfm25-8b-a1b | 1 | 12/12 | `core-v2` | `a7e0e31bedd8` |

- **adhoc** — temperature 1.0, top_p 0.95, seed 42, fallback cap 8,192 tokens (pinned)

Sample *n* of a task uses `seed + n - 1`, so independent samples are independent while the run stays repeatable. Backends differ in how honestly they honour a seed: llama.cpp with a fixed seed and a warm cache is close to deterministic, some hosted providers ignore it entirely. The sample-stability rows above are how you find out which kind you are talking to.

## Integrity

- **adhoc**: 2 first answers hit the token cap
- **adhoc**: 3 grader runs produced no `RESULT` line
- **adhoc**: 1 answer had no code fence and were graded verbatim
- **adhoc**: 1 answer ended inside an unclosed fence (salvaged)
- **adhoc**: complete — 12 of 12 expected records, no duplicates

## Reproducing this report

```bash
# one target from your modelbench.toml
modelbench run --target adhoc --suite core-v2 --samples 1 --out runs/adhoc
modelbench report runs/adhoc
```

Exact prompts, raw model output and extracted solutions for every record are stored next to `results.jsonl` in each run directory (`s<N>/raw/`, `s<N>/sol/`).
