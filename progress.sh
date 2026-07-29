#!/usr/bin/env bash
# Progress of the running Lean+Mathlib arm (GPT-5.4 -> Sonnet -> DeepSeek).
OUT=/tmp/claude-1000/-home-prem-practical-work-ai/c7b29ff4-ae86-4aef-88bb-abc62d16ca5c/tasks/bc4bqfnwi.output
DB=/home/prem/practical-work-ai/results/experiments.db

phase=$(grep -oE '(GPT-5.4|SONNET|DEEPSEEK)[^#]*' "$OUT" | tail -1)
last=$(grep -oE '\[ *[0-9]+/[0-9]+\]' "$OUT" | tail -1)
passed=$(grep -c 'PASSED' "$OUT")

echo "phase: ${phase:-<starting>}"
echo "cell : ${last:-<starting>}   passed(attempts): $passed"
echo "--- cost by model (live from DB, ALL arms combined) ---"
python3 -c "import sqlite3;c=sqlite3.connect('$DB');\
[print(f'  {m:<20} cells={n:<3} \${u}') for (m,n,u) in c.execute('SELECT model_name,COUNT(DISTINCT COALESCE(parent_run_id,id)),ROUND(SUM(cost_usd),2) FROM runs GROUP BY model_name')];\
print('  TOTAL \$%.2f' % (c.execute('SELECT COALESCE(SUM(cost_usd),0) FROM runs').fetchone()[0]))"
echo "--- mathlib-arm rows so far ---"
python3 -c "import sqlite3;print('  ', c) if False else print('  mathlib runs:', sqlite3.connect('$DB').execute(\"SELECT COUNT(*) FROM runs WHERE lean_library='mathlib'\").fetchone()[0])"
echo "--- last 2 lines ---"
tail -n 2 "$OUT"
