# modelbench — lfm25-1.2b on core-v2

Single run on suite `core-v2`: **8.6%** mean first-attempt task score, 0.0% of attempts fully solved before feedback.

_Generated 2026-10-20T00:25:31 by modelbench 2.1.0. Suite: `core-v2`. _

## Headline

Scores are means over tasks (each task weighs the same), then over samples. `first` is the answer before any feedback; `final` allows one repair turn in which only failing assertion messages are returned.

| metric | adhoc |
|---|---|
| records / expected | 12 / 12 |
| samples / task | 1 |
| mean task score, first | 8.6% |
| 95% CI, first · final | 0.0–20.2% · 2.7–24.0% |
| mean task score, final | 12.0% |
| first-attempt assertions | 11/79 (13.9%) |
| fully solved, first | 0.0% |
| fully solved, final | 0.0% |
| repair turns / improved / solved | 12 / 2 / 0 |
| median call wall | 2.1s |
| p90 call wall | 4.2s |
| median output tokens / call | 444 |
| prompt tokens, total | 25,638 |
| completion tokens, total | 10,208 |
| wall clock, total | 0.8 min |
| median decode speed | 221.8 tok/s |
| median TTFT | 0.05s |
| answers cut by token cap | 0 |

## Per task

| task | category | adhoc | best |
|---|---|---|---|
| t01_weighted_jobs | algorithms | 0.0% | adhoc |
| t02_text_justify | spec | 0.0% | adhoc |
| t03_json_parser | parsing | 0.0% | adhoc |
| t04_sql_report | sql | 25.0% | adhoc |
| t05_async_pool | async | 16.7% | adhoc |
| t06_repo_bugfix | repo | 0.0% | adhoc |
| t07_thread_queue | concurrency | 0.0% | adhoc |
| t08_code_review | review | 0.0% | adhoc |
| t09_csv_rfc4180 | parsing | 0.0% | adhoc |
| t10_pairs_refactor | refactor | 61.5% | adhoc |
| t11_varint_protocol | binary | 0.0% | adhoc |
| t12_ledger_feature | longcontext | 0.0% | adhoc |

## Per category

| category | adhoc |
|---|---|
| algorithms | 0.0% |
| async | 16.7% |
| binary | 0.0% |
| concurrency | 0.0% |
| longcontext | 0.0% |
| parsing | 0.0% |
| refactor | 61.5% |
| repo | 0.0% |
| review | 0.0% |
| spec | 0.0% |
| sql | 25.0% |

## Where it fails

Failing assertions from the first attempt, counted once per record and grouped by assertion name. A name that fails in both samples of a task is a systematic gap, not noise.

| assertion | adhoc |
|---|---|
| `100 random cases` | 1 record, 1 task |
| `200k zeros under 1.5s` | 1 record, 1 task |
| `basic` | 1 record, 1 task |
| `calls fn with item and index` | 1 record, 1 task |
| `does not mutate items` | 1 record, 1 task |
| `duplicates` | 1 record, 1 task |
| `empty resolves [] without calls` | 1 record, 1 task |
| `exhausted retries rejects with last error` | 1 record, 1 task |
| `fail-fast stops starting new items` | 1 record, 1 task |
| `import BoundedQueue and QueueClosed` | 1 record, 1 task |
| `import and parse_json exists` | 1 record, 1 task |
| `import encode_varints/decode_varints` | 1 record, 1 task |

## Provenance

| run | endpoint | served id | samples | records | suite | digest |
|---|---|---|---|---|---|---|
| adhoc | http://127.0.0.1:8080/v1 | lfm25-1.2b | 1 | 12/12 | `core-v2` | `a7e0e31bedd8` |

- **adhoc** — temperature 1.0, top_p 0.95, seed 42, fallback cap 8,192 tokens (pinned)

Sample *n* of a task uses `seed + n - 1`, so independent samples are independent while the run stays repeatable. Backends differ in how honestly they honour a seed: llama.cpp with a fixed seed and a warm cache is close to deterministic, some hosted providers ignore it entirely. The sample-stability rows above are how you find out which kind you are talking to.

## Integrity

- **adhoc**: 2 grader runs produced no `RESULT` line
- **adhoc**: complete — 12 of 12 expected records, no duplicates

## Reproducing this report

```bash
# one target from your modelbench.toml
modelbench run --target adhoc --suite core-v2 --samples 1 --out runs/adhoc
modelbench report runs/adhoc
```

Exact prompts, raw model output and extracted solutions for every record are stored next to `results.jsonl` in each run directory (`s<N>/raw/`, `s<N>/sol/`).
