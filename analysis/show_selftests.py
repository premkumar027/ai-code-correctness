"""Inspect the Python self-tests arm.

    # overview: one line per combo, plus per-model aggregates
    uv run python analysis/show_selftests.py

    # the actual code a model wrote, and what the hidden suite said about it
    uv run python analysis/show_selftests.py --run 946
    uv run python analysis/show_selftests.py --task obs_table_closed --style naive

    # only the interesting cases: self-consistent but actually wrong
    uv run python analysis/show_selftests.py --gap
"""

import argparse
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.extract import extract_impl_and_tests  # noqa: E402

DB = PROJECT_ROOT / "results" / "experiments.db"
LANG = "Python (self-tests)"


def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def combos(conn):
    """One row per combo (the best attempt), mirroring the best-of-5 rule.

    A combo is a (model, task, style) family: attempt 1 is the root run and
    attempts 2-5 are children with parent_run_id = root id.
    """
    return conn.execute(
        """
        WITH fam AS (
            SELECT COALESCE(r.parent_run_id, r.id) AS root,
                   r.id, r.model_name, r.task_name, r.prompt_style,
                   r.attempt_number, r.response_time, r.cost_usd,
                   e.total_tests, e.tests_passed,
                   e.hidden_total, e.hidden_passed,
                   e.ref_tests_total, e.ref_tests_passed,
                   e.mutants_total, e.mutants_caught
            FROM runs r JOIN evaluations e ON e.run_id = r.id
            WHERE r.language = ?
        )
        SELECT root,
               model_name, task_name, prompt_style,
               MAX(attempt_number)                    AS attempts,
               SUM(response_time)                     AS total_time,
               SUM(COALESCE(cost_usd, 0))             AS cost,
               -- the final attempt decides the combo
               (SELECT total_tests       FROM fam f2 WHERE f2.root = fam.root
                 ORDER BY attempt_number DESC LIMIT 1) AS own_total,
               (SELECT tests_passed      FROM fam f2 WHERE f2.root = fam.root
                 ORDER BY attempt_number DESC LIMIT 1) AS own_passed,
               (SELECT hidden_total      FROM fam f2 WHERE f2.root = fam.root
                 ORDER BY attempt_number DESC LIMIT 1) AS hid_total,
               (SELECT hidden_passed     FROM fam f2 WHERE f2.root = fam.root
                 ORDER BY attempt_number DESC LIMIT 1) AS hid_passed,
               (SELECT ref_tests_total   FROM fam f2 WHERE f2.root = fam.root
                 ORDER BY attempt_number DESC LIMIT 1) AS ref_total,
               (SELECT ref_tests_passed  FROM fam f2 WHERE f2.root = fam.root
                 ORDER BY attempt_number DESC LIMIT 1) AS ref_passed,
               (SELECT mutants_total     FROM fam f2 WHERE f2.root = fam.root
                 ORDER BY attempt_number DESC LIMIT 1) AS mut_total,
               (SELECT mutants_caught    FROM fam f2 WHERE f2.root = fam.root
                 ORDER BY attempt_number DESC LIMIT 1) AS mut_caught,
               (SELECT id                FROM fam f2 WHERE f2.root = fam.root
                 ORDER BY attempt_number DESC LIMIT 1) AS final_run_id
        FROM fam
        GROUP BY root
        ORDER BY model_name, task_name, prompt_style
        """,
        (LANG,),
    ).fetchall()


def pct(num, den):
    return f"{num / den * 100:.0f}%" if den else "  -"


def overview(rows, only_gap=False):
    if not rows:
        print(f"No rows with language = '{LANG}' yet.")
        return

    print(f"{'model':<17}{'task':<24}{'style':<18}{'att':>4}"
          f"{'own':>8}{'hidden':>9}{'valid':>8}{'mut':>8}{'sec':>7}")
    print("-" * 103)
    for r in rows:
        self_ok = r["own_total"] and r["own_passed"] == r["own_total"]
        true_ok = r["hid_total"] and r["hid_passed"] == r["hid_total"]
        if only_gap and not (self_ok and not true_ok):
            continue
        flag = "  <-- self-consistent but WRONG" if self_ok and not true_ok else ""
        own = f"{r['own_passed']}/{r['own_total']}"
        hid = f"{r['hid_passed']}/{r['hid_total']}"
        ref = f"{r['ref_passed']}/{r['ref_total']}"
        mut = f"{r['mut_caught']}/{r['mut_total']}" if r["mut_total"] else "-"
        print(
            f"{r['model_name']:<17}{r['task_name']:<24}{r['prompt_style']:<18}"
            f"{r['attempts']:>4}{own:>8}{hid:>9}{ref:>8}{mut:>8}"
            f"{r['total_time']:>7.0f}{flag}"
        )

    if only_gap:
        return

    print()
    print("PER MODEL")
    print(f"{'model':<17}{'combos':>7}{'SelfOK':>8}{'TrueOK':>8}{'Gap':>5}"
          f"{'ValidTests':>12}{'Mutation':>10}{'Cost':>9}{'Time':>8}")
    print("-" * 84)
    for model in sorted({r["model_name"] for r in rows}):
        sub = [r for r in rows if r["model_name"] == model]
        self_ok = sum(1 for r in sub if r["own_total"] and r["own_passed"] == r["own_total"])
        true_ok = sum(1 for r in sub if r["hid_total"] and r["hid_passed"] == r["hid_total"])
        valid = sum(1 for r in sub if r["ref_total"] and r["ref_passed"] == r["ref_total"])
        caught = sum(r["mut_caught"] or 0 for r in sub)
        pool = sum(r["mut_total"] or 0 for r in sub)
        valid_cell = f"{valid}/{len(sub)}"
        print(f"{model:<17}{len(sub):>7}{self_ok:>8}{true_ok:>8}{self_ok - true_ok:>5}"
              f"{valid_cell:>12}{pct(caught, pool):>10}"
              f"{sum(r['cost'] for r in sub):>8.2f}${sum(r['total_time'] for r in sub):>7.0f}s")

    print()
    print("  own        = the model's own tests, on its own code  (pass criterion,")
    print("               the analogue of Lean's 'compiles && no sorry')")
    print("  hidden     = our human suite in tasks/*/  (ground-truth correctness,")
    print("               scored silently, never shown to the model)")
    print("  valid      = its tests run against the known-correct reference.py")
    print("               (a failure means the TEST is wrong, not the code)")
    print("  mut        = seeded real defects its tests caught (test strength;")
    print("               an escaped mutant is the analogue of a vacuous theorem)")
    print("  Gap        = SelfOK - TrueOK = believed itself correct but was not")


def show_one(conn, run_id=None, task=None, style=None, model=None):
    if run_id:
        row = conn.execute(
            "SELECT * FROM runs WHERE id = ?", (run_id,)
        ).fetchone()
    else:
        sql = "SELECT * FROM runs WHERE language = ?"
        params = [LANG]
        for col, val in (("task_name", task), ("prompt_style", style), ("model_name", model)):
            if val:
                sql += f" AND {col} = ?"
                params.append(val)
        sql += " ORDER BY id DESC LIMIT 1"
        row = conn.execute(sql, params).fetchone()

    if not row:
        print("No matching run.")
        return

    ev = conn.execute("SELECT * FROM evaluations WHERE run_id = ?", (row["id"],)).fetchone()
    print(f"run {row['id']}  {row['model_name']}  {row['task_name']}  "
          f"{row['prompt_style']}  attempt {row['attempt_number']}")
    print(f"time {row['response_time']:.1f}s  cost ${row['cost_usd'] or 0:.4f}  "
          f"tokens in/out {row['input_tokens']}/{row['output_tokens']}")
    if ev:
        print(f"own {ev['tests_passed']}/{ev['total_tests']}   "
              f"hidden {ev['hidden_passed']}/{ev['hidden_total']}   "
              f"valid {ev['ref_tests_passed']}/{ev['ref_tests_total']}   "
              f"mutants {ev['mutants_caught']}/{ev['mutants_total']}")

    impl, tests = extract_impl_and_tests(row["response"])
    print("\n" + "=" * 78 + "\nIMPLEMENTATION IT WROTE\n" + "=" * 78)
    print(impl or "(could not be parsed)")
    print("\n" + "=" * 78 + "\nTESTS IT WROTE\n" + "=" * 78)
    print(tests or "(could not be parsed)")
    if ev and ev["notes"]:
        print("\n" + "=" * 78 + "\nWHAT ITS OWN TESTS REPORTED\n" + "=" * 78)
        print(ev["notes"][:2500])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=int, help="show one run's implementation and tests")
    ap.add_argument("--task")
    ap.add_argument("--style", choices=("naive", "structured", "chain_of_thought"))
    ap.add_argument("--model")
    ap.add_argument("--gap", action="store_true",
                    help="only combos that passed their own tests but failed the hidden suite")
    args = ap.parse_args()

    conn = connect()
    if args.run or (args.task and args.style):
        show_one(conn, args.run, args.task, args.style, args.model)
    else:
        overview(combos(conn), only_gap=args.gap)


if __name__ == "__main__":
    main()
