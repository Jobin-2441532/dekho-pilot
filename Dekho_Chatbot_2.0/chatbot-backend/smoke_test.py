"""
Smoke test — runs against the live server on port 8001.
Updated for OpenRouter + Groq multi-provider setup.

Run:  python smoke_test.py
Requires: server running with `uvicorn app.main:app --port 8001`
"""
import urllib.request
import json
import time

BASE = "http://localhost:8001"


def get(path):
    r = urllib.request.urlopen(BASE + path, timeout=10)
    return json.loads(r.read())


def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}
    )
    r = urllib.request.urlopen(req, timeout=30)
    return json.loads(r.read())


errors = []

# ── 1. Health ──────────────────────────────────────────────────────────────────
try:
    h = get("/health")
    print("1. HEALTH:", h["status"])
    for k, v in h["services"].items():
        ok = v.startswith("ok") or "mock" in v or "disabled" in v
        tag = "OK" if ok else "FAIL"
        print(f"     [{tag}] {k}: {v}")
        if not ok:
            errors.append(f"Health {k}: {v}")
except Exception as e:
    print("1. HEALTH: FAILED -", e)
    errors.append(str(e))

# ── 2. Context endpoint ────────────────────────────────────────────────────────
print()
try:
    ctx = get("/api/chat/context/user_priya")
    name = ctx["user"]["name"]
    income = ctx["user"]["monthly_income"]
    spent = ctx["current_month"]["total_expenses"]
    goals = len(ctx["goals"])
    alerts = len(ctx["budget_alerts"])
    print(f"2. CONTEXT (Priya): name={name}, income={income}, spent={spent}, goals={goals}, alerts={alerts}")
except Exception as e:
    print("2. CONTEXT: FAILED -", e)
    errors.append(str(e))

# ── 3. Chat endpoint (covers intent detection + LLM + response package) ─────────
print()
print("3. CHAT ENDPOINT:")
tests = [
    ("user_priya",  "How am I doing this month?",        "BALANCE_OVERVIEW"),
    ("user_arjun",  "Am I over budget?",                  "BUDGET_STATUS"),
    ("user_meera",  "How much did I spend on food?",      "SPENDING_QUERY"),
    ("user_priya",  "Show my spending trend",             "TREND_ANALYSIS"),
    ("user_arjun",  "I spent 500 at Zomato",              "ADD_TRANSACTION"),
    ("user_priya",  "How can I save more?",               "ADVICE_REQUEST"),
]
for user, q, expected_intent in tests:
    try:
        t0 = time.time()
        resp = post("/api/chat", {"user_id": user, "message": q, "session_id": "smoke_" + user})
        ms = int((time.time() - t0) * 1000)
        text = (resp.get("text") or "")[:70].replace("\n", " ")
        intent = resp.get("intent", "?")
        chips = len(resp.get("quick_replies") or [])
        fallback = resp.get("is_fallback", False)
        intent_ok = intent == expected_intent
        intent_tag = "OK" if intent_ok else f"WARN (expected {expected_intent})"
        print(f"     [{user}] {intent} [{intent_tag}] | {ms}ms | chips={chips} | fallback={fallback}")
        print(f"       > {text}")
        if not resp.get("text"):
            errors.append(f"No text from {user}")
    except Exception as e:
        print(f"     [{user}] FAILED: {e}")
        errors.append(str(e))

# ── 4. Streaming endpoint (basic check — reads first event) ────────────────────
print()
print("4. STREAM ENDPOINT:")
try:
    data = json.dumps({"user_id": "user_priya", "message": "How am I doing?", "session_id": "smoke_stream"}).encode()
    req = urllib.request.Request(
        BASE + "/api/chat/stream", data=data, headers={"Content-Type": "application/json"}
    )
    r = urllib.request.urlopen(req, timeout=30)
    raw = r.read().decode("utf-8")
    has_token = "event: token" in raw
    has_done  = "event: done" in raw
    print(f"     has_token={has_token} | has_done={has_done}")
    if not has_token:
        errors.append("Stream: no token event received")
    if not has_done:
        errors.append("Stream: no done event received")
except Exception as e:
    print("     FAILED -", e)
    errors.append(str(e))

# ── 5. History ─────────────────────────────────────────────────────────────────
print()
try:
    hist = get("/api/chat/history/user_priya?session_id=smoke_user_priya")
    print(f"5. HISTORY: {len(hist['messages'])} messages stored")
except Exception as e:
    print("5. HISTORY: FAILED -", e)
    errors.append(str(e))

# ── 6. Session cleanup ─────────────────────────────────────────────────────────
print()
try:
    for sid in ["smoke_user_priya", "smoke_user_arjun", "smoke_user_meera", "smoke_stream"]:
        req = urllib.request.Request(
            f"{BASE}/api/chat/session/{sid}",
            method="DELETE",
        )
        urllib.request.urlopen(req, timeout=10)
    print("6. SESSION CLEANUP: OK")
except Exception as e:
    print("6. SESSION CLEANUP: FAILED -", e)

# ── Result ─────────────────────────────────────────────────────────────────────
print()
if errors:
    print(f"FAILED - {len(errors)} error(s):")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
else:
    print("ALL CHECKS PASSED")
