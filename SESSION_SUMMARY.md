# Session Summary / Restart Point — 2026-07-08

Handoff for the AI Code Correctness & Usability project (JKU Linz practical work).
All data lives in `results/experiments.db` (SQLite: tables `runs`, `evaluations`, `annotations`).

---

## What this session accomplished

1. **Finished the Lean data generation** — ran DeepSeek + mathlib (the last Lean arm).
2. **Started & finished the Python arm** for all 3 models that have Lean data.
3. **Built the correctness analysis** — `analysis/analysis.ipynb` with 8 figures.

---

## Current data state (as of 2026-07-08)

`experiments.db`: **888 runs / 888 evaluations / 0 annotations**. 296 combos total.

### Pass-rate grid (best-of-5, impossible tasks excluded)

| model | Python | Lean (none) | Lean (mathlib) |
|-------|:------:|:-----------:|:--------------:|
| gpt-5.4  | 100% | 56% | 52% |
| sonnet   | 100% | 38% | 59% |
| deepseek | 100% | 31%* | 49%* |

\*DeepSeek no-lib/mathlib read 35%/48% when impossible tasks are *included* (raw). The notebook excludes them from pass-rate charts by design.

**Headline finding:** Python is saturated (100% for all models) — the entire difficulty signal is in the Lean formalization, where models drop to 31–59%.

### Arms completed
- **Lean no-lib:** gpt-5.4 (27 combos), sonnet (26), deepseek (48, full-16 tasks)
- **Lean mathlib:** gpt-5.4 (27), sonnet (27), deepseek (48, full-16)
- **Python:** gpt-5.4 (27 combos, 9 tasks, $0.24), sonnet (27, 9 tasks, $0.86), deepseek (39, 13 tasks, $0.15) — all 100%

Python scope = intersection of each model's Lean tasks with Python-available tasks
(gpt/sonnet = 9 automata tasks; deepseek = 13 = its 16 Lean tasks minus 3 Lean-only `impossible_*`).

**Total spend so far: ~$20.59** (sonnet $11.63, gpt $3.97, deepseek $5.00).

---

## Key facts / gotchas

- **`language` column values are `'Lean 4'` and `'Python'`** (capitalized) — NOT lowercase. Filter accordingly.
- **Pass criterion:** Python = `total_tests>0 AND tests_passed==total_tests`; Lean = `compiles==1 AND sorry_count==0`. A combo passes if *any* attempt passes (best-of-5).
- **Combo family:** root run has `parent_run_id IS NULL` (attempt 1); refinement attempts 2–5 are children with `parent_run_id = root id`. Root id of any run = `parent_run_id if set else id`.
- **Impossible tasks** (`impossible_*`, Lean-only): a compiled proof with no `sorry` is a RED FLAG (model "proved" the unprovable), not a success.
- **Anthropic credits were topped up 2026-07-08** — Claude/Sonnet runs work again (previously failing with 400 "credit balance too low").
- **Deleting a bad run:** remove rows from BOTH `runs` AND `evaluations` (run_id FK, no cascade).
- cslib Lean arm skipped (disk space).

---

## How to run things

**Generate data** (orchestrator, appends to experiments.db):
```
uv run python src/orchestrator.py --model <name> --task <t> [--task <t> ...] \
    --language python                       # Python arm
uv run python src/orchestrator.py --model <name> --task <t> ... \
    --language lean --lean-library mathlib  # Lean arm (or --lean-library none)
```
Add `--dry-run` to preview combos without API calls. Models: gpt-5.5, gpt-5.4-mini,
gpt-5.4, claude-opus-4-7, claude-sonnet-4-6, gemini-2.5-flash, gemini-3.5-flash,
gemma-4-27b, deepseek-v4-pro. Prompt styles: naive, structured, chain_of_thought (all run by default).

**Re-run the analysis notebook:**
```
cd analysis && uv run --with jupyter --with nbconvert \
    jupyter nbconvert --to notebook --execute --inplace analysis.ipynb
```
Figures land in `analysis/figures/` (8 PNGs).

---

## Analysis notebook (`analysis/analysis.ipynb`)

7 sections, all executed with output:
1. Pass-rate grid (model × config)
2. Refinement loop — attempt-1 vs best-of-5
3. mathlib effect (per-model delta, matched tasks)
4. Impossible-task flag rate (honesty signal)
5. Prompt style (naive/structured/chain_of_thought)
6. Cost & latency per combo
7. Per-task difficulty (Lean)

Deps added this session: `pandas`, `matplotlib` (in `pyproject.toml`).

---

---

## Python self-tests arm (added 2026-07-29) — built, NOT yet run

**Why.** The original Python arm is not comparable with the Lean arm. Three
confounds, in order of importance:

1. **Who writes the spec.** Lean: the model writes implementation + theorem +
   proof. Python: the model writes only the implementation and is graded against
   *our* hidden suite. This alone explains most of "Python 100% vs Lean 31–59%".
2. **Verification strength.** Lean pass = `compiles && sorry_count==0`, which
   never checks that the theorem *says* anything — a weak theorem, honestly
   proved, passes. Python's fixed suite cannot be gamed that way.
3. **Hidden interface contract.** 39 of 93 attempt-1 Python runs collected 0
   tests purely because the model's function names did not match what
   `conftest.py` imports. Those measure API guessing, not correctness — and the
   refinement loop then leaked the expected interface through the pytest error.

The existing Python arm stays as the **control / upper bound**: "when the spec is
given and only implementation is required, all three models saturate."

**The new arm** (`--self-tests`) makes the model author the implementation *and*
~10 tests, mirroring Lean. Stored under `language = 'Python (self-tests)'`, so
every existing query and the notebook are untouched.

| | Lean | Python (given tests) | Python (self-tests) |
|---|---|---|---|
| model produces | impl + theorem + proof | impl | impl + 10 tests |
| machine check | compiles, no `sorry` | hidden suite passes | its own tests pass |
| spec author | model | us | model |
| ground truth | none | the suite itself | hidden suite, scored silently |

**Three measurements per attempt** (new `evaluations` columns):

- `total_tests` / `tests_passed` — the model's OWN tests. The pass criterion,
  analogous to `compiles && no sorry`.
- `hidden_total` / `hidden_passed` — our human suite = real correctness. **The gap
  between this and the pass criterion is the headline result.**
- `ref_tests_total` / `ref_tests_passed` — its tests run against the known-correct
  `reference.py`. Failure here means the test itself is wrong.
- `mutants_total` / `mutants_caught` — test strength: share of real seeded defects
  its tests catch. Escaped mutant ≈ vacuous theorem. This is the quantitative
  "test quality vs proof quality" comparison.

**Validity rule:** the hidden suite NEVER enters the refinement loop. Feedback is
derived only from the model's own failing tests, mirroring Lean where the model
only sees compiler output on its own goal. Leaking it would rebuild confound 3.

**Mutation testing** (`src/evaluation/mutation.py`). Mutants of `reference.py` are
kept only if the human suite detects them (proving each is a real, catchable
defect), then ranked **subtlest first** — by how much of the human suite still
passes. This ranking is what makes the metric work: with an AST-ordered pool a
deliberately vacuous suite scored 90% on merge_sort, because catastrophic mutants
are caught even by type-and-length assertions. Ranked by subtlety, the same three
suites score 100% / 92% / 67%. Pools are cached in `results/mutants/<task>.json`.
Prebuild with `uv run python -m src.evaluation.mutation` (no API cost).

Mutation score is computed only on attempts that matter (a passing attempt, or the
last one), since each score costs one pytest run per mutant.

**Run it:**
```
./run_python_selftests.sh                       # all 3 models, Lean-matched scope
uv run python src/orchestrator.py --self-tests --model gpt-5.4 --task merge_sort
```
Est. ~$3 total (output tokens roughly double vs the given-tests arm).

**Also added:** `--with-interface` states the required API in the *given-tests*
prompt, fixing confound 3 for that arm. Off by default because the existing 93
combos were collected without it — that arm needs a re-run (~$1.25) to stay
comparable on attempt-1 rates and latency.

**Footnote on the executor:** generated code is run by the `pytest` on PATH, which
here is a **system Python 3.10** install, not the project's 3.12 venv. All 888
existing runs used it. Do not `uv add pytest` — the venv binary would win the PATH
lookup in `python_runner.py` and silently move new runs to 3.12, making them
incomparable with existing data. `tests/conftest.py` stubs `dotenv` for this reason.

---

## NEXT STEPS (pick up here)

1. **Usability analysis — the big open item.** The `annotations` table has **0 rows**. Columns:
   `readability, theorem_quality, test_quality, manual_fixes, reusable, fits_signature, fixable, notes`.
   This is the "Usability" half of the project title and is entirely unstarted.
   **Decision needed:** human review vs LLM-assisted (LLM judge scores the generated code,
   then spot-check). Once decided, build a review harness that writes into `annotations`,
   then add a usability section to the notebook.

2. **(Optional) More Python models** — gemini-2.5/3.5-flash, gemma-4-27b, gpt-5.5, gpt-5.4-mini,
   opus-4-7. None have Lean data, so no scope to match → would run the full 18 Python tasks.
   Cheap (~$0.15–1 each for most; opus/gpt-5.5 pricier).

3. **(Optional) cslib Lean arm** — skipped for disk space.

---

## Backups (in `results/`)
- `experiments_backup_beforeStrayDelete_2026-07-08.db` (latest — before removing 5 stray bfs/binary_search rows from an aborted full-18-task python run)
- `_beforeDeepseekMathlib_2026-07-05.db`
- `_beforeSonnetMathlibReset_2026-07-04.db`
- `_leannone_2026-07-03.db`
- `_pilot_backup_2026-05.db`

## Run logs (in `logs/`)
`deepseek_mathlib_*.log`, `python_gpt54_*.log`, `python_sonnet_*.log`, `python_deepseek_*.log`
