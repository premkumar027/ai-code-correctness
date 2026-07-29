#!/usr/bin/env bash
# Lean + Mathlib arm, fast-first: GPT-5.4 (9) -> Sonnet (9) -> DeepSeek (16).
# Mirrors the no-lib coverage. Appends to results/experiments.db.
cd /home/prem/practical-work-ai

NINE="--task prefix_closed_create --task prefix_closed_minimal --task prefix_closed_concat \
--task suffix_closed_create --task suffix_closed_minimal --task suffix_closed_concat \
--task obs_table_build --task obs_table_oracle --task obs_table_closed"

SIXTEEN="$NINE --task obs_table_consistent \
--task obs_table_dfa_build --task obs_table_dfa_sublanguage --task obs_table_dfa_behavior \
--task impossible_prefix_suffix_concat --task impossible_dfa_exact --task impossible_prefix_is_suffix"

echo "########## GPT-5.4 — mathlib — 9 tasks ##########"
uv run python src/orchestrator.py --model gpt-5.4 $NINE --language lean --lean-library mathlib

echo "########## SONNET — mathlib — 9 tasks ##########"
uv run python src/orchestrator.py --model claude-sonnet-4-6 $NINE --language lean --lean-library mathlib

echo "########## DEEPSEEK — mathlib — 16 tasks (SLOW, ~overnight) ##########"
uv run python src/orchestrator.py --model deepseek-v4-pro $SIXTEEN --language lean --lean-library mathlib

echo "########## MATHLIB ARM DONE ##########"
