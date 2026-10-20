# modelbench — bonsai2-4b on core-v2

Single run on suite `core-v2`: **35.5%** mean first-attempt task score, 16.7% of attempts fully solved before feedback.

_Generated 2026-10-20T01:22:21 by modelbench 2.1.0. Suite: `core-v2`. _

## Headline

Scores are means over tasks (each task weighs the same), then over samples. `first` is the answer before any feedback; `final` allows one repair turn in which only failing assertion messages are returned.

| metric | adhoc |
|---|---|
| records / expected | 12 / 12 |
| samples / task | 1 |
| mean task score, first | 35.5% |
| 95% CI, first · final | 13.5–61.4% · 20.8–72.4% |
| mean task score, final | 45.8% |
| first-attempt assertions | 95/261 (36.4%) |
| fully solved, first | 16.7% |
| fully solved, final | 25.0% |
| repair turns / improved / solved | 10 / 2 / 1 |
| median call wall | 45.7s |
| p90 call wall | 85.5s |
| median output tokens / call | 5494 |
| prompt tokens, total | 32,920 |
| completion tokens, total | 142,240 |
| tokens per solved task | 47413 |
| wall clock, total | 22.6 min |
| median decode speed | 127.7 tok/s |
| median TTFT | 0.28s |
| answers cut by token cap | 1 |

## Per task

| task | category | adhoc | best |
|---|---|---|---|
| t01_weighted_jobs | algorithms | 0.0% | adhoc |
| t02_text_justify | spec | 100.0% | adhoc |
| t03_json_parser | parsing | 0.0% | adhoc |
| t04_sql_report | sql | 90.5% | adhoc |
| t05_async_pool | async | 0.0% | adhoc |
| t06_repo_bugfix | repo | 64.0% | adhoc |
| t07_thread_queue | concurrency | 0.0% | adhoc |
| t08_code_review | review | 71.4% | adhoc |
| t09_csv_rfc4180 | parsing | 0.0% | adhoc |
| t10_pairs_refactor | refactor | 100.0% | adhoc |
| t11_varint_protocol | binary | 0.0% | adhoc |
| t12_ledger_feature | longcontext | 0.0% | adhoc |

## Per category

| category | adhoc |
|---|---|
| algorithms | 0.0% |
| async | 0.0% |
| binary | 0.0% |
| concurrency | 0.0% |
| longcontext | 0.0% |
| parsing | 0.0% |
| refactor | 100.0% |
| repo | 64.0% |
| review | 71.4% |
| spec | 100.0% |
| sql | 90.5% |

## Where it fails

Failing assertions from the first attempt, counted once per record and grouped by assertion name. A name that fails in both samples of a task is a systematic gap, not noise.

| assertion | adhoc |
|---|---|
| `28 nights discount` | 1 record, 1 task |
| `28 nights total` | 1 record, 1 task |
| `basic` | 1 record, 1 task |
| `fri+sat total` | 1 record, 1 task |
| `friday night is weekend` | 1 record, 1 task |
| `half-up discount and tax` | 1 record, 1 task |
| `ledger imports` | 1 record, 1 task |
| `load module` | 1 record, 1 task |
| `missing pricing_is_comparison (pricing.py` | 1 record, 1 task |
| `missing pricing_tax_on_gross (pricing.py` | 1 record, 1 task |
| `sunday night is weekday` | 1 record, 1 task |
| `thu+fri+sat room total` | 1 record, 1 task |

## Provenance

| run | endpoint | served id | samples | records | suite | digest |
|---|---|---|---|---|---|---|
| adhoc | http://127.0.0.1:8081/v1 | bonsai2-4b | 1 | 12/12 | `core-v2` | `a7e0e31bedd8` |

- **adhoc** — temperature 1.0, top_p 0.95, seed 42, fallback cap 8,192 tokens (pinned)

Sample *n* of a task uses `seed + n - 1`, so independent samples are independent while the run stays repeatable. Backends differ in how honestly they honour a seed: llama.cpp with a fixed seed and a warm cache is close to deterministic, some hosted providers ignore it entirely. The sample-stability rows above are how you find out which kind you are talking to.

## Integrity

- **adhoc**: 1 first answer hit the token cap
- **adhoc**: 5 grader runs produced no `RESULT` line
- **adhoc**: complete — 12 of 12 expected records, no duplicates

## Reproducing this report

```bash
# one target from your modelbench.toml
modelbench run --target adhoc --suite core-v2 --samples 1 --out runs/adhoc
modelbench report runs/adhoc
```

Exact prompts, raw model output and extracted solutions for every record are stored next to `results.jsonl` in each run directory (`s<N>/raw/`, `s<N>/sol/`).
