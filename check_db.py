import sqlite3
conn = sqlite3.connect(r'c:\Dekho App\Dekho\backend\dekho.db')
for table in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    print(f'\n=== {table[0]} ===')
    cols = conn.execute(f'PRAGMA table_info({table[0]})').fetchall()
    for c in cols:
        print(f'  {c[1]} ({c[2]})')

# Also try inserting a test row to see exact error
print('\n\n=== TEST INSERT ===')
try:
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions
            (user_id, date, description, amount, direction, merchant, category,
             sub_category, payment_mode, vpa, confidence, raw_sms, needs_review, source)
        VALUES (1, '2026-05-01', 'Zomato', 450.0, 'debit', 'Zomato', 'Food & Dining',
                'Food Delivery', 'UPI', NULL, 0.88, 'test sms', 0, 'sms')
    """)
    conn.commit()
    print('INSERT OK - row id:', cur.lastrowid)
except Exception as e:
    print('INSERT FAILED:', e)

# Count transactions
total = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
print('Total transactions in DB:', total)
conn.close()
