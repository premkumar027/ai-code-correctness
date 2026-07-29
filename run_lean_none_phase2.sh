#!/usr/bin/env bash
# Phase 2 of the Lean-none arm: DeepSeek full, then GPT-5.4 trimmed.
# Appends to results/experiments.db (alongside Sonnet's partial run).
cd /home/prem/practical-work-ai

echo "########## DEEPSEEK — full 16 tasks ##########"
uv run python src/orchestrator.py \
  --model deepseek-v4-pro \
  --task prefix_closed_create --task prefix_closed_minimal --task prefix_closed_concat \
  --task suffix_closed_create --task suffix_closed_minimal --task suffix_closed_concat \
  --task obs_table_build --task obs_table_oracle --task obs_table_closed --task obs_table_consistent \
  --task obs_table_dfa_build --task obs_table_dfa_sublanguage --task obs_table_dfa_behavior \
  --task impossible_prefix_suffix_concat --task impossible_dfa_exact --task impossible_prefix_is_suffix \
  --language lean --lean-library none

echo "########## GPT-5.4 — trimmed 9 tasks (prefix/suffix + obs build/oracle/closed) ##########"
uv run python src/orchestrator.py \
  --model gpt-5.4 \
  --task prefix_closed_create --task prefix_closed_minimal --task prefix_closed_concat \
  --task suffix_closed_create --task suffix_closed_minimal --task suffix_closed_concat \
  --task obs_table_build --task obs_table_oracle --task obs_table_closed \
  --language lean --lean-library none

echo "########## PHASE 2 DONE ##########"
