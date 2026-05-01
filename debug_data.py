"""
Deep debug: shows exactly what the user sees (or doesn't see) in the UI.
Run AFTER the backend is started.
"""
import sqlite3

DB = r'c:\Dekho App\Dekho\backend\dekho.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("=" * 60)
print("USERS IN DB")
print("=" * 60)
users = conn.execute("SELECT id, name, email FROM users").fetchall()
for u in users:
    print(f"  id={u['id']} | {u['name']} | {u['email']}")

print()
print("=" * 60)
print("ALL TRANSACTIONS IN DB")
print("=" * 60)
txns = conn.execute("""
    SELECT id, user_id, date, merchant, amount, direction, category, review_status, source_type
    FROM transactions ORDER BY id DESC
""").fetchall()
if not txns:
    print("  *** NO TRANSACTIONS FOUND ***")
else:
    for t in txns:
        print(f"  id={t['id']} user={t['user_id']} {t['date']} | {t['merchant']} | "
              f"Rs{t['amount']} {t['direction']} | {t['category']} | {t['review_status']} | {t['source_type']}")

print()
print("=" * 60)
print("DASHBOARD API SIMULATION (user_id=1, direction=debit, this month)")
print("=" * 60)
from datetime import date
month_start = date(date.today().year, date.today().month, 1).isoformat()
print(f"  from_date filter = '{month_start}'")

rows = conn.execute("""
    SELECT id, date, merchant, amount, direction, category
    FROM transactions
    WHERE user_id = 1 AND direction = 'debit' AND date >= ?
    ORDER BY date DESC
""", (month_start,)).fetchall()
print(f"  Rows matching (user_id=1, debit, >= {month_start}): {len(rows)}")
for r in rows:
    print(f"    #{r['id']} | {r['date']} | {r['merchant']} | Rs{r['amount']} | {r['category']}")

conn.close()
