import urllib.request, json, sqlite3, urllib.error

BASE = "http://localhost:8000"

# 1. Login
form = 'username=jobin%40dekho.com&password=dekho123'
req = urllib.request.Request(f'{BASE}/api/v1/auth/login', data=form.encode(),
    headers={'Content-Type': 'application/x-www-form-urlencoded'}, method='POST')
try:
    token = json.loads(urllib.request.urlopen(req).read())['access_token']
    print("LOGIN: OK")
except Exception as e:
    print("LOGIN FAIL:", e); exit()

headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

# 2. Classify SMS (goes through proxy → ML service → DB insert)
sms_tests = [
    "INR 450.00 debited from A/c XX1234 on 01-05-2026. Info: ZOMATO. Avl Bal: INR 12,345.00",
    "Rs.1200 debited from your account. Info: UBER. Available balance: Rs.45,000",
    "INR 2500.00 credited to your account from SALARY HDFC on 01-05-2026",
]

for sms in sms_tests:
    data = json.dumps({'sms_text': sms}).encode()
    req2 = urllib.request.Request(f'{BASE}/api/v1/ml/classify', data=data, headers=headers, method='POST')
    try:
        resp = json.loads(urllib.request.urlopen(req2).read())
        db_err = resp.get('db_error', '')
        print(f"SMS INGEST: ₹{resp.get('amount')} | {resp.get('category')} | id={resp.get('id')} | db_error={db_err or 'NONE'}")
    except urllib.error.HTTPError as e:
        print(f"SMS FAIL: HTTP {e.code} — {e.read().decode()[:100]}")

# 3. Check transactions in DB
conn = sqlite3.connect(r'c:\Dekho App\Dekho\backend\dekho.db')
rows = conn.execute('SELECT id, date, merchant, amount, category, direction FROM transactions ORDER BY id DESC LIMIT 5').fetchall()
conn.close()

print(f"\nDB transactions: {len(rows)}")
for r in rows:
    print(f"  #{r[0]} | {r[1]} | {r[2]} | ₹{r[3]} | {r[4]} | {r[5]}")

# 4. Check via API (dashboard transactions list)
req3 = urllib.request.Request(f'{BASE}/api/v1/dashboard/transactions?limit=5', headers=headers)
resp3 = json.loads(urllib.request.urlopen(req3).read())
print(f"\nDashboard API total: {resp3.get('total')} transactions")
for tx in resp3.get('data', []):
    print(f"  {tx.get('date')} | {tx.get('merchant')} | ₹{tx.get('amount')} | {tx.get('category')}")
