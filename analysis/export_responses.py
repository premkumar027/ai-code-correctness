"""Export every LLM response to a browsable file tree so the generated code can be
read and verified by hand.

Layout:
    analysis/responses/<config>/<model>/<task>/<style>/a<attempt>_<PASS|FAIL>.<ext>
    analysis/responses/<config>/<model>/<task>/<style>/a<attempt>_<PASS|FAIL>.raw.md

- <config>      Python | Lean4-none | Lean4-mathlib
- .<ext> file   the EXTRACTED code that was actually compiled/tested (.py or .lean),
                with a header comment carrying the metadata + evaluation result.
- .raw.md file  the full unedited model response (prose + code fences).

Also writes analysis/responses/INDEX.csv with one row per run.

Run:  cd analysis && uv run python export_responses.py
"""
import csv
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.orchestrator import extract_code, extract_lean_code  # exact same extraction as the runner

HERE = Path(__file__).resolve().parent
DB = HERE.parent / "results" / "experiments.db"
OUT = HERE / "responses"


def safe(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in str(s))


def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT r.id, r.model_name, r.task_name, r.language, r.lean_library,
               r.prompt_style, r.attempt_number, r.response, r.error,
               e.total_tests, e.tests_passed, e.compiles, e.sorry_count
        FROM runs r LEFT JOIN evaluations e ON e.run_id = r.id
        ORDER BY r.model_name, r.task_name, r.language, r.lean_library,
                 r.prompt_style, r.attempt_number
        """
    ).fetchall()
    con.close()

    if OUT.exists():
        import shutil
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    index = []
    n_files = 0
    for r in rows:
        is_lean = str(r["language"]).startswith("Lean")
        if is_lean:
            config = f"Lean4-{r['lean_library'] or 'none'}"
            ext, comment = "lean", "--"
            code = extract_lean_code(r["response"] or "")
            sc = r["sorry_count"]
            passed = (r["compiles"] == 1) and (sc is not None and sc == 0)
            verdict = f"compiles={r['compiles']} sorry={r['sorry_count']}"
        else:
            config = "Python"
            ext, comment = "py", "#"
            code = extract_code(r["response"] or "")
            tp, tt = r["tests_passed"], r["total_tests"]
            passed = (tt or 0) > 0 and tp == tt
            verdict = f"tests={tp}/{tt}"

        tag = "PASS" if passed else ("ERROR" if r["error"] else "FAIL")
        d = OUT / safe(config) / safe(r["model_name"]) / safe(r["task_name"]) / safe(r["prompt_style"])
        d.mkdir(parents=True, exist_ok=True)
        base = f"a{r['attempt_number']}_{tag}"

        header = (
            f"{comment} run_id={r['id']}  model={r['model_name']}  task={r['task_name']}\n"
            f"{comment} config={config}  style={r['prompt_style']}  attempt={r['attempt_number']}\n"
            f"{comment} RESULT: {tag}  ({verdict})\n"
            f"{comment} {'-' * 60}\n\n"
        )
        (d / f"{base}.{ext}").write_text(header + (code or "(empty)"), encoding="utf-8")
        (d / f"{base}.raw.md").write_text(r["response"] or "(no response — API error)", encoding="utf-8")
        n_files += 1

        rel = (d / f"{base}.{ext}").relative_to(OUT)
        index.append({
            "run_id": r["id"], "model": r["model_name"], "task": r["task_name"],
            "config": config, "style": r["prompt_style"], "attempt": r["attempt_number"],
            "result": tag, "detail": verdict, "file": str(rel),
        })

    with open(OUT / "INDEX.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(index[0].keys()))
        w.writeheader()
        w.writerows(index)

    print(f"Exported {n_files} runs -> {OUT}")
    print(f"Index: {OUT / 'INDEX.csv'}  ({len(index)} rows)")
    # quick per-config counts
    from collections import Counter
    c = Counter((row["config"], row["result"]) for row in index)
    for (cfg, res), k in sorted(c.items()):
        print(f"  {cfg:16} {res:6} {k}")


if __name__ == "__main__":
    main()
