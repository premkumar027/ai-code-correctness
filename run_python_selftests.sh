#!/usr/bin/env bash
# Python arm where the MODEL writes the tests too — the symmetric counterpart of
# the Lean arm (implementation + theorem + proof). Appends to results/experiments.db
# under language = 'Python (self-tests)', so the existing 'Python' rows and all
# current analysis are untouched.
#
# Task scope matches each model's Lean scope so the comparison is per-task matched:
# GPT-5.4 and Sonnet ran 9 tasks in Lean, DeepSeek ran 16 (13 of which have a
# Python counterpart — the 3 impossible_* tasks are Lean-only).
#
# Prebuild the mutation pools first (one-time, no API cost):
#   uv run python -m src.evaluation.mutation
cd /home/prem/practical-work-ai

NINE="--task prefix_closed_create --task prefix_closed_minimal --task prefix_closed_concat \
--task suffix_closed_create --task suffix_closed_minimal --task suffix_closed_concat \
--task obs_table_build --task obs_table_oracle --task obs_table_closed"

THIRTEEN="$NINE --task obs_table_consistent \
--task obs_table_dfa_build --task obs_table_dfa_sublanguage --task obs_table_dfa_behavior"

echo "########## GPT-5.4 — self-authored tests — 9 tasks ##########"
uv run python src/orchestrator.py --model gpt-5.4 $NINE --self-tests

echo "########## SONNET — self-authored tests — 9 tasks ##########"
uv run python src/orchestrator.py --model claude-sonnet-4-6 $NINE --self-tests

echo "########## DEEPSEEK — self-authored tests — 13 tasks ##########"
uv run python src/orchestrator.py --model deepseek-v4-pro $THIRTEEN --self-tests

echo "########## PYTHON SELF-TESTS ARM DONE ##########"
