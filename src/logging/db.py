import sqlite3
from datetime import datetime
from pathlib import Path

from src.config import estimate_cost

DB_PATH = Path("results/experiments.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))

    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            model_name TEXT,
            task_name TEXT,
            language TEXT,
            lean_library TEXT,
            prompt_style TEXT,
            prompt_text TEXT,
            response TEXT,
            response_time REAL,
            error TEXT,
            parent_run_id INTEGER,
            attempt_number INTEGER DEFAULT 1,
            feedback_given TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            cost_usd REAL
        )
    """)

    # migrate existing databases that predate later columns
    for column, coltype in (
        ("lean_library", "TEXT"),
        ("input_tokens", "INTEGER"),
        ("output_tokens", "INTEGER"),
        ("cost_usd", "REAL"),
    ):
        try:
            conn.execute(f"ALTER TABLE runs ADD COLUMN {column} {coltype}")
            conn.commit()
        except Exception:
            pass  # column already exists
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            total_tests INTEGER,
            tests_passed INTEGER,
            compiles INTEGER,
            sorry_count INTEGER,
            uses_mathlib INTEGER,
            notes TEXT,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
    """)

    # Human-judged (manual) metrics, filled in during a review pass — NOT by the
    # orchestrator. Scores are nullable so partial annotation is fine.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            reviewer TEXT,
            readability INTEGER,        -- 1-5
            theorem_quality INTEGER,    -- 1-5: coverage, guarantees not too strong
            test_quality INTEGER,       -- 1-5: edge cases covered
            manual_fixes INTEGER,       -- number of edits needed to make it work
            reusable INTEGER,           -- 1-5: easy to reuse
            fits_signature INTEGER,     -- 0/1: matches a given API/method signature
            fixable INTEGER,            -- 0/1: a mismatched/impossible theorem could be fixed
            notes TEXT,
            created_at TEXT,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
    """)

    conn.commit()
    return conn

def save_run(model_name, task_name, language, prompt_style, prompt_text,
             response, response_time, error=None, parent_run_id=None,
             attempt_number=1, feedback_given=None, lean_library=None,
             input_tokens=0, output_tokens=0):
    cost_usd = estimate_cost(model_name, input_tokens, output_tokens)
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO runs (timestamp, model_name, task_name, language,
            lean_library, prompt_style, prompt_text, response, response_time,
            error, parent_run_id, attempt_number, feedback_given,
            input_tokens, output_tokens, cost_usd)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            model_name,
            task_name,
            language,
            lean_library,
            prompt_style,
            prompt_text,
            response,
            response_time,
            error,
            parent_run_id,
            attempt_number,
            feedback_given,
            input_tokens,
            output_tokens,
            cost_usd,
        ),
    )
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id


def save_evaluation(run_id, total_tests=0, tests_passed=0, compiles=None,
                    sorry_count=None, uses_mathlib=None, notes=""):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO evaluations (run_id, total_tests, tests_passed,
            compiles, sorry_count, uses_mathlib, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, total_tests, tests_passed, compiles, sorry_count,
         uses_mathlib, notes),
    )
    conn.commit()
    conn.close()


def save_annotation(run_id, reviewer=None, readability=None, theorem_quality=None,
                    test_quality=None, manual_fixes=None, reusable=None,
                    fits_signature=None, fixable=None, notes=""):
    """Record a manual review of a run. All scores optional; call during review."""
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO annotations (run_id, reviewer, readability, theorem_quality,
            test_quality, manual_fixes, reusable, fits_signature, fixable,
            notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, reviewer, readability, theorem_quality, test_quality,
         manual_fixes, reusable, fits_signature, fixable, notes,
         datetime.now().isoformat()),
    )
    annotation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return annotation_id


def get_annotations(run_id=None):
    """All annotations, or just those for one run_id."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    if run_id is None:
        rows = conn.execute("SELECT * FROM annotations ORDER BY id").fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM annotations WHERE run_id = ? ORDER BY id", (run_id,)
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_runs():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM runs ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_run_chain(parent_id):
    """Get all attempts for a single generation (attempt 1 + all follow-ups)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT * FROM runs
        WHERE id = ? OR parent_run_id = ?
        ORDER BY attempt_number ASC
        """,
        (parent_id, parent_id),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]