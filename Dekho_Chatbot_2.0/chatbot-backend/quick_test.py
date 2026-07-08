"""
Dekho Chatbot — Quick pre-launch test (rate-limit test excluded).
Runs all critical checks in ~3 minutes.
"""
import requests, time, uuid, json, sys, io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_URL = "http://localhost:8001"
TIMEOUT = 25
RESULTS = []

def record(name, passed, detail=""):
    RESULTS.append((name, passed, detail))
    tag = "[PASS]" if passed else "[FAIL]"
    detail_out = detail[:200] if detail else ""
    print(f"{tag} {name}" + (f" -- {detail_out}" if detail_out else ""))

def chat(user_id, message, session_id=None):
    payload = {"user_id": user_id, "message": message}
    if session_id:
        payload["session_id"] = session_id
    return requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=TIMEOUT)

# 1. Health
print("\n-- 1. Health check --")
r = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
data = r.json()
svcs = data.get("services", {})
record("health_reachable", r.status_code == 200, json.dumps(svcs))
has_gemini = any("gemini" in k.lower() for k in svcs.keys())
record("health_reports_gemini", has_gemini,
       "Gemini NOT in /health -- no visibility on secondary fallback" if not has_gemini else "ok")

# 2. Intent coverage
print("\n-- 2. Intent coverage (10 intents) --")
INTENT_CASES = [
    ("BALANCE_OVERVIEW",  "How am I doing this month?"),
    ("SPENDING_QUERY",    "How much did I spend on food this month?"),
    ("BUDGET_STATUS",     "Am I over budget?"),
    ("GOAL_PROGRESS",     "How close am I to my vacation goal?"),
    ("ANOMALY_ALERT",     "Anything unusual in my spending?"),
    ("ADVICE_REQUEST",    "Any tips to save more?"),
    ("COMPARISON_QUERY",  "How does this month compare to last month?"),
    ("TREND_ANALYSIS",    "Is my spending trend improving?"),
    ("GENERAL_CHAT",      "hi there"),
    ("OUT_OF_SCOPE",      "What is the weather today?"),
]
for expected, msg in INTENT_CASES:
    try:
        r = chat("user_priya", msg)
        actual = r.json().get("intent") if r.status_code == 200 else f"HTTP_{r.status_code}"
        record(f"intent::{expected}", actual == expected, f"{msg!r} -> got {actual!r}")
    except Exception as e:
        record(f"intent::{expected}", False, str(e))

# 3. Transaction false-confirmation regression
print("\n-- 3. Critical: transaction regression (no false confirmations) --")
BAD_PHRASES = [
    "added to your", "has been added", "successfully logged", "logged it",
    "saved to your", "done!", "recorded your", "transaction added",
    "i've added", "i've logged",
]
TX_MSGS = [
    "I spent 500 at Zomato",
    "Add 5000 to my vacation fund",
    "I paid 1200 for groceries at Blinkit",
    "log a 300 rupee Uber ride",
]
for msg in TX_MSGS:
    try:
        r = chat("user_priya", msg)
        if r.status_code != 200:
            record(f"tx_intent::{msg[:40]}", False, f"HTTP {r.status_code}")
            continue
        d = r.json()
        intent = d.get("intent")
        text = d.get("text", "")
        text_lower = text.lower()
        record(f"tx_routes_OUT_OF_SCOPE::{msg[:40]}", intent == "OUT_OF_SCOPE", f"got intent={intent!r}")
        bad = next((p for p in BAD_PHRASES if p in text_lower), None)
        record(f"tx_no_false_confirmation::{msg[:40]}", bad is None,
               f'BAD phrase: "{bad}"' if bad else f"clean -- {text[:120]!r}")
    except Exception as e:
        record(f"tx_error::{msg[:40]}", False, str(e))

# 4. Cache correctness
print("\n-- 4. Cache correctness (food vs transport within same window) --")
try:
    r1 = chat("user_meera", "How much did I spend on food this month?")
    r2 = chat("user_meera", "How much did I spend on transport this month?")
    if r1.status_code == 200 and r2.status_code == 200:
        t1, t2 = r1.json().get("text", ""), r2.json().get("text", "")
        record("cache_food_vs_transport_distinct", t1 != t2,
               "SAME text returned -- cache bug!" if t1 == t2 else "Distinct answers confirmed")
    else:
        record("cache_food_vs_transport_distinct", False, f"HTTP {r1.status_code}/{r2.status_code}")
except Exception as e:
    record("cache_food_vs_transport_distinct", False, str(e))

# 5. Auth dev-mode
print("\n-- 5. Auth dev-mode (no header required) --")
r = requests.post(f"{BASE_URL}/api/chat", json={"user_id":"user_priya","message":"hi"}, timeout=TIMEOUT)
record("auth_dev_mode_no_header_ok", r.status_code == 200, f"HTTP {r.status_code}")

# 6. Session persistence
print("\n-- 6. Session persistence --")
try:
    sid = str(uuid.uuid4())
    chat("user_priya", "How am I doing this month?", sid)
    chat("user_priya", "What about my goals?", sid)
    r = requests.get(f"{BASE_URL}/api/chat/history/user_priya", params={"session_id": sid}, timeout=TIMEOUT)
    msgs = r.json() if r.status_code == 200 else []
    record("session_history_persists", r.status_code == 200 and len(msgs) >= 2,
           f"HTTP {r.status_code}, messages stored={len(msgs)}")
except Exception as e:
    record("session_history_persists", False, str(e))

# 7. Feedback loop
print("\n-- 7. Feedback + preference learning --")
try:
    r_chat = chat("user_arjun", "How much did I spend on food?")
    if r_chat.status_code == 200:
        sid2 = r_chat.json().get("session_id")
        fb = {"user_id":"user_arjun","session_id":sid2,"message_id":str(uuid.uuid4()),
              "rating":"down","correction":"that was transport not food","intent":"SPENDING_QUERY"}
        r_fb = requests.post(f"{BASE_URL}/api/chat/feedback", json=fb, timeout=TIMEOUT)
        record("feedback_submission", r_fb.status_code == 200, f"HTTP {r_fb.status_code}")
        r_prefs = requests.get(f"{BASE_URL}/api/chat/preferences/user_arjun", timeout=TIMEOUT)
        if r_prefs.status_code == 200:
            corrections = r_prefs.json().get("corrections", [])
            found = any("transport" in c.lower() for c in corrections)
            record("correction_stored_in_prefs", found, f"corrections={corrections}")
        else:
            record("correction_stored_in_prefs", False, f"HTTP {r_prefs.status_code}")
    else:
        record("feedback_submission", False, "chat call failed")
except Exception as e:
    record("feedback_submission", False, str(e))

# Summary
print("\n" + "=" * 60)
passed = sum(1 for _,p,_ in RESULTS if p)
total = len(RESULTS)
print(f"RESULT: {passed}/{total} checks passed")
failed = [(n,d) for n,p,d in RESULTS if not p]
if failed:
    print("\nFAILED CHECKS:")
    for n,d in failed:
        print(f"  FAIL  {n}")
        if d: print(f"        {d}")
sys.exit(0 if not failed else 1)
