import os
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse

# Load database URL from backend/.env instead of hardcoding
from dotenv import load_dotenv
load_dotenv("backend/.env")

LOCAL_DB_URL = os.getenv("LOCAL_DATABASE_URL", "postgresql://dekho:dekho_password@localhost:5432/dekho_pilot")
NEON_DB_URL = os.getenv("DATABASE_URL")

if not NEON_DB_URL or "ep-ancient-haze" in NEON_DB_URL:
    print("Warning: Target DATABASE_URL is not set or points to the previous original project database.")
    print("Migration aborted to protect the original production database.")
    print("Please set a new fresh pilot DATABASE_URL in backend/.env to run this migration.")
    exit(1)

print(f"Source PG : {LOCAL_DB_URL}")
print(f"Target PG : {NEON_DB_URL}")

# Parse URLs
r_local = urlparse(LOCAL_DB_URL)
r_neon = urlparse(NEON_DB_URL)

# Connect to both DBs
try:
    pg_local = psycopg2.connect(
        host=r_local.hostname, port=r_local.port or 5432,
        dbname=r_local.path.lstrip('/'), user=r_local.username, password=r_local.password
    )
    pg_neon = psycopg2.connect(
        host=r_neon.hostname, port=r_neon.port or 5432,
        dbname=r_neon.path.lstrip('/'), user=r_neon.username, password=r_neon.password,
        sslmode='require'
    )
    print("Successfully connected to both databases.")
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

cur_local = pg_local.cursor()
cur_neon = pg_neon.cursor()

def get_tables(cursor):
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    return [r[0] for r in cursor.fetchall()]

local_tables = get_tables(cur_local)
neon_tables = get_tables(cur_neon)

if not neon_tables:
    print("Neon database is completely empty. We need to create tables first!")
    print("Let's run SQLAlchemy create_all before running this.")
    exit(1)

for table in local_tables:
    cur_local.execute(f"SELECT * FROM {table}")
    rows = cur_local.fetchall()
    
    if not rows:
        print(f"  {table}: 0 rows — skipping")
        continue

    # Get column names
    col_names = [desc[0] for desc in cur_local.description]
    
    # Wipe target
    cur_neon.execute(f"TRUNCATE {table} RESTART IDENTITY CASCADE")
    
    # Insert
    placeholders = ", ".join(["%s"] * len(col_names))
    col_str = ", ".join(col_names)
    sql = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"
    
    psycopg2.extras.execute_batch(cur_neon, sql, rows)
    pg_neon.commit()
    print(f"  {table}: {len(rows)} rows migrated to Neon")

# Sync sequences
print("\nSyncing sequences...")
for tbl in local_tables:
    # Attempt to sync ID sequence if ID column exists
    if "id" in col_names: # just a rough check
        try:
            cur_neon.execute(f"SELECT setval(pg_get_serial_sequence('{tbl}','id'), COALESCE(MAX(id),0)+1, false) FROM {tbl}")
            pg_neon.commit()
            print(f"  {tbl}.id sequence synced")
        except Exception:
            pg_neon.rollback()

pg_local.close()
pg_neon.close()
print("\nMigration complete! All your local data is now in the cloud!")
