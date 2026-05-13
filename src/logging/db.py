import sqlite3
from datetime import datetime
from pathlib import Path

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
            prompt_style TEXT,
            prompt_text TEXT,
            response TEXT,
            response_time REAL,
            error TEXT,
            parent_run_id INTEGER,
            attempt_number INTEGER DEFAULT 1,
            feedback_given TEXT
        )
    """)
    
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

    conn.commit()
    return conn

def save_run(model_name, task_name, language, prompt_style, prompt_text,
             response, response_time, error=None, parent_run_id=None,
             attempt_number=1, feedback_given=None):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO runs (timestamp, model_name, task_name, language,
            prompt_style, prompt_text, response, response_time, error,
            parent_run_id, attempt_number, feedback_given)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            model_name,
            task_name,
            language,
            prompt_style,
            prompt_text,
            response,
            response_time,
            error,
            parent_run_id,
            attempt_number,
            feedback_given,
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