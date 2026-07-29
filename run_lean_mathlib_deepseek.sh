#!/usr/bin/env bash
# Mathlib arm — DeepSeek only (full 16 tasks). GPT-5.4 and Sonnet already done.
# Appends to results/experiments.db. Run after PC restart to finish the mathlib arm.
# NOTE: this is the SLOW one (~overnight). Safe to re-run; only DeepSeek/mathlib is generated.
cd /home/prem/practical-work-ai

SIXTEEN="--task prefix_closed_create --task prefix_closed_minimal --task prefix_closed_concat \
--task suffix_closed_create --task suffix_closed_minimal --task suffix_closed_concat \
--task obs_table_build --task obs_table_oracle --task obs_table_closed --task obs_table_consistent \
--task obs_table_dfa_build --task obs_table_dfa_sublanguage --task obs_table_dfa_behavior \
--task impossible_prefix_suffix_concat --task impossible_dfa_exact --task impossible_prefix_is_suffix"

echo "########## DEEPSEEK — mathlib — 16 tasks (SLOW, ~overnight) ##########"
uv run python src/orchestrator.py --model deepseek-v4-pro $SIXTEEN --language lean --lean-library mathlib

echo "########## DEEPSEEK MATHLIB DONE ##########"
