# modelbench — lfm25-24b-a2b on core-v2

Single run on suite `core-v2`: **58.0%** mean first-attempt task score, 50.0% of attempts fully solved before feedback.

_Generated 2026-10-20T02:36:11 by modelbench 2.1.0. Suite: `core-v2`. _

## Headline

Scores are means over tasks (each task weighs the same), then over samples. `first` is the answer before any feedback; `final` allows one repair turn in which only failing assertion messages are returned.

| metric | adhoc |
|---|---|
| records / expected | 12 / 12 |
| samples / task | 1 |
| mean task score, first | 58.0% |
| 95% CI, first · final | 33.0–83.3% · 47.5–94.7% |
| mean task score, final | 72.0% |
| first-attempt assertions | 148/176 (84.1%) |
| fully solved, first | 50.0% |
| fully solved, final | 50.0% |
| repair turns / improved / solved | 6 / 2 / 0 |
| median call wall | 92.6s |
| p90 call wall | 137.2s |
| median output tokens / call | 10919 |
| prompt tokens, total | 24,733 |
| completion tokens, total | 315,662 |
| tokens per solved task | 52610 |
| wall clock, total | 44.5 min |
| median decode speed | 118.5 tok/s |
| median TTFT | 0.08s |
| answers cut by token cap | 4 |

## Per task

| task | category | adhoc | best |
|---|---|---|---|
| t01_weighted_jobs | algorithms | 100.0% | adhoc |
| t02_text_justify | spec | 100.0% | adhoc |
| t03_json_parser | parsing | 0.0% | adhoc |
| t04_sql_report | sql | 100.0% | adhoc |
| t05_async_pool | async | 0.0% | adhoc |
| t06_repo_bugfix | repo | 96.0% | adhoc |
| t07_thread_queue | concurrency | 0.0% | adhoc |
| t08_code_review | review | 100.0% | adhoc |
| t09_csv_rfc4180 | parsing | 0.0% | adhoc |
| t10_pairs_refactor | refactor | 100.0% | adhoc |
| t11_varint_protocol | binary | 0.0% | adhoc |
| t12_ledger_feature | longcontext | 100.0% | adhoc |

## Per category

| category | adhoc |
|---|---|
| algorithms | 100.0% |
| async | 0.0% |
| binary | 0.0% |
| concurrency | 0.0% |
| longcontext | 100.0% |
| parsing | 0.0% |
| refactor | 100.0% |
| repo | 96.0% |
| review | 100.0% |
| spec | 100.0% |
| sql | 100.0% |

## Where it fails

Failing assertions from the first attempt, counted once per record and grouped by assertion name. A name that fails in both samples of a task is a systematic gap, not noise.

| assertion | adhoc |
|---|---|
| `half-up discount and tax` | 1 record, 1 task |
| `import and parse_json exists` | 1 record, 1 task |
| `import encode_varints/decode_varints` | 1 record, 1 task |
| `import parse_csv and write_csv` | 1 record, 1 task |
| `load module` | 1 record, 1 task |

## Provenance

| run | endpoint | served id | samples | records | suite | digest |
|---|---|---|---|---|---|---|
| adhoc | http://127.0.0.1:8080/v1 | lfm25-24b-a2b | 1 | 12/12 | `core-v2` | `a7e0e31bedd8` |

- **adhoc** — temperature 1.0, top_p 0.95, seed 42, fallback cap 8,192 tokens (pinned)

Sample *n* of a task uses `seed + n - 1`, so independent samples are independent while the run stays repeatable. Backends differ in how honestly they honour a seed: llama.cpp with a fixed seed and a warm cache is close to deterministic, some hosted providers ignore it entirely. The sample-stability rows above are how you find out which kind you are talking to.

## Integrity

- **adhoc**: 4 first answers hit the token cap
- **adhoc**: 1 grader run produced no `RESULT` line
- **adhoc**: 1 answer ended inside an unclosed fence (salvaged)
- **adhoc**: complete — 12 of 12 expected records, no duplicates

## Reproducing this report

```bash
# one target from your modelbench.toml
modelbench run --target adhoc --suite core-v2 --samples 1 --out runs/adhoc
modelbench report runs/adhoc
```

Exact prompts, raw model output and extracted solutions for every record are stored next to `results.jsonl` in each run directory (`s<N>/raw/`, `s<N>/sol/`).
