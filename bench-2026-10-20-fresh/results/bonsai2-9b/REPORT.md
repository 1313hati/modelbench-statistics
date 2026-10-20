# modelbench — bonsai2-9b on core-v2

Single run on suite `core-v2`: **45.1%** mean first-attempt task score, 16.7% of attempts fully solved before feedback.

_Generated 2026-10-20T01:28:45 by modelbench 2.1.0. Suite: `core-v2`. _

## Headline

Scores are means over tasks (each task weighs the same), then over samples. `first` is the answer before any feedback; `final` allows one repair turn in which only failing assertion messages are returned.

| metric | adhoc |
|---|---|
| records / expected | 12 / 12 |
| samples / task | 1 |
| mean task score, first | 45.1% |
| 95% CI, first · final | 21.1–70.4% · 21.9–72.1% |
| mean task score, final | 46.2% |
| first-attempt assertions | 113/233 (48.5%) |
| fully solved, first | 16.7% |
| fully solved, final | 33.3% |
| repair turns / improved / solved | 10 / 2 / 2 |
| median call wall | 115.9s |
| p90 call wall | 186.6s |
| median output tokens / call | 10225 |
| prompt tokens, total | 29,142 |
| completion tokens, total | 296,927 |
| tokens per solved task | 74232 |
| wall clock, total | 59.8 min |
| median decode speed | 87.9 tok/s |
| median TTFT | 0.19s |
| answers cut by token cap | 4 |

## Per task

| task | category | adhoc | best |
|---|---|---|---|
| t01_weighted_jobs | algorithms | 100.0% | adhoc |
| t02_text_justify | spec | 94.4% | adhoc |
| t03_json_parser | parsing | 8.5% | adhoc |
| t04_sql_report | sql | 92.9% | adhoc |
| t05_async_pool | async | 16.7% | adhoc |
| t06_repo_bugfix | repo | 72.0% | adhoc |
| t07_thread_queue | concurrency | 0.0% | adhoc |
| t08_code_review | review | 57.1% | adhoc |
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
| parsing | 4.3% |
| refactor | 100.0% |
| repo | 72.0% |
| review | 57.1% |
| spec | 94.4% |
| sql | 92.9% |

## Where it fails

Failing assertions from the first attempt, counted once per record and grouped by assertion name. A name that fails in both samples of a task is a systematic gap, not noise.

| assertion | adhoc |
|---|---|
| `28 nights discount` | 1 record, 1 task |
| `28 nights total` | 1 record, 1 task |
| `array` | 1 record, 1 task |
| `bare fraction` | 1 record, 1 task |
| `basic` | 1 record, 1 task |
| `calls fn with item and index` | 1 record, 1 task |
| `does not mutate items` | 1 record, 1 task |
| `duplicate keys last wins` | 1 record, 1 task |
| `empty array` | 1 record, 1 task |
| `empty document` | 1 record, 1 task |
| `empty object` | 1 record, 1 task |
| `empty resolves [] without calls` | 1 record, 1 task |

## Provenance

| run | endpoint | served id | samples | records | suite | digest |
|---|---|---|---|---|---|---|
| adhoc | http://127.0.0.1:8080/v1 | bonsai2-9b | 1 | 12/12 | `core-v2` | `a7e0e31bedd8` |

- **adhoc** — temperature 1.0, top_p 0.95, seed 42, fallback cap 8,192 tokens (pinned)

Sample *n* of a task uses `seed + n - 1`, so independent samples are independent while the run stays repeatable. Backends differ in how honestly they honour a seed: llama.cpp with a fixed seed and a warm cache is close to deterministic, some hosted providers ignore it entirely. The sample-stability rows above are how you find out which kind you are talking to.

## Integrity

- **adhoc**: 4 first answers hit the token cap
- **adhoc**: 2 grader runs produced no `RESULT` line
- **adhoc**: complete — 12 of 12 expected records, no duplicates

## Reproducing this report

```bash
# one target from your modelbench.toml
modelbench run --target adhoc --suite core-v2 --samples 1 --out runs/adhoc
modelbench report runs/adhoc
```

Exact prompts, raw model output and extracted solutions for every record are stored next to `results.jsonl` in each run directory (`s<N>/raw/`, `s<N>/sol/`).
