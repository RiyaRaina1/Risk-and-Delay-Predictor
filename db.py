import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "risk.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Projects table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        owner TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """)

    # Metrics snapshots (historical)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        snapshot_date TEXT NOT NULL,              -- YYYY-MM-DD
        planned_tasks INTEGER NOT NULL,
        completed_tasks INTEGER NOT NULL,
        in_progress_tasks INTEGER NOT NULL,
        blockers_count INTEGER NOT NULL,
        bugs_open INTEGER NOT NULL,
        scope_change_percent REAL NOT NULL,       -- 0..100
        avg_cycle_time_days REAL NOT NULL,        -- e.g., 1.5
        comments TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()