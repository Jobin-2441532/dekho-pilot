"""
migrate_sqlite_to_pg.py
Copies all data from dekho.db (SQLite) into the PostgreSQL database.
Run ONCE after switching DATABASE_URL to PostgreSQL.
"""
import sqlite3, psycopg2, psycopg2.extras, os, sys
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load .env
load_dotenv(Path("backend/.env"))
DB_URL = os.getenv("DATABASE_URL")
SQLITE_PATH = Path("backend/dekho.db")

if not SQLITE_PATH.exists():
    print(f"❌  SQLite file not found at {SQLITE_PATH} — nothing to migrate")
    sys.exit(0)

print(f"📦  Source SQLite : {SQLITE_PATH}")
print(f"🐘  Target PG     : {DB_URL}")
print()

# ── Connections ──────────────────────────────────────────────────────────────
sl = sqlite3.connect(str(SQLITE_PATH))
sl.row_factory = sqlite3.Row

r = urlparse(DB_URL)
pg = psycopg2.connect(host=r.hostname, port=r.port or 5432,
                      dbname=r.path.lstrip('/'), user=r.username, password=r.password)
pg.autocommit = False
cur = pg.cursor()

# ── Helper ────────────────────────────────────────────────────────────────────
def migrate_table(table, columns, pg_columns=None):
    pg_columns = pg_columns or columns
    rows = sl.execute(f"SELECT {','.join(columns)} FROM {table}").fetchall()
    if not rows:
        print(f"  {table}: no rows — skipping")
        return

    # Wipe target to avoid duplicates on re-run
    cur.execute(f"TRUNCATE {table} RESTART IDENTITY CASCADE")

    bool_cols = {"is_recurring","is_refund","is_cashback","is_income","is_transfer","is_wallet_load"}
    placeholders = ", ".join(["%s"] * len(pg_columns))
    col_str = ", ".join(pg_columns)
    sql = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"
    def cast_row(row):
        return tuple(bool(row[c]) if c in bool_cols else row[c] for c in columns)
    data = [cast_row(row) for row in rows]
    psycopg2.extras.execute_batch(cur, sql, data)
    print(f"  ✅  {table}: {len(data)} rows migrated")

# ── Migrate each table ────────────────────────────────────────────────────────
print("Migrating tables...")

# users
migrate_table("users", [
    "id", "name", "email", "password_hash",
    "income_range", "goal_type", "risk_comfort",
    "monthly_budget", "financial_stage", "created_at",
])

# transactions (all columns present in SQLite)
sl_cols = [r[1] for r in sl.execute("PRAGMA table_info(transactions)").fetchall()]
common = [c for c in sl_cols if c not in ("description",)]  # drop if exists
migrate_table("transactions", common)

# savings_goals
sg_cols = [r[1] for r in sl.execute("PRAGMA table_info(savings_goals)").fetchall()]
if sg_cols:
    migrate_table("savings_goals", sg_cols)

# budgets
bg_cols = [r[1] for r in sl.execute("PRAGMA table_info(budgets)").fetchall()]
if bg_cols:
    migrate_table("budgets", bg_cols)

# assets
a_cols = [r[1] for r in sl.execute("PRAGMA table_info(assets)").fetchall()]
if a_cols:
    migrate_table("assets", a_cols)

# recommendations
rec_cols = [r[1] for r in sl.execute("PRAGMA table_info(recommendations)").fetchall()]
if rec_cols:
    migrate_table("recommendations", rec_cols)

pg.commit()

# Sync sequences so new auto-increment IDs don't clash
print("\nSyncing sequences...")
for tbl, col in [("users","id"),("transactions","id"),("savings_goals","id"),
                  ("budgets","id"),("assets","id"),("recommendations","id")]:
    try:
        cur.execute(f"SELECT setval(pg_get_serial_sequence('{tbl}','{col}'), COALESCE(MAX({col}),0)+1, false) FROM {tbl}")
        pg.commit()
        print(f"  ✅  {tbl}.{col} sequence synced")
    except Exception as e:
        pg.rollback()
        print(f"  ⚠️   {tbl}: {e}")

sl.close()
pg.close()
print("\n🎉  Migration complete! All SQLite data is now in PostgreSQL.")
