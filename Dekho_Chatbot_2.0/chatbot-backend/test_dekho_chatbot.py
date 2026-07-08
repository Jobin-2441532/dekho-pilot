"""
Dekho Chatbot v2.1 — Pre-Launch Test Script
=============================================
Run this against your locally running chatbot backend to verify the
blocker fixes claimed in dekho_chatbot_reference.md (v2.1, 1 July 2026)
actually hold, before shipping to the first 10-100 user cohort.

USAGE:
    pip install requests
    python test_dekho_chatbot.py

Assumes (per the reference doc):
    - Server running at http://localhost:8001
    - AUTH_ENABLED=false (dev mode)
    - USE_MOCK_DATA=true
    - Test users: user_priya, user_arjun, user_meera

This script does NOT assume the fixes are correct — it tries to
disprove each claim. A "PASS" here means the specific failure mode
we previously identified did not reproduce. It does not mean the
feature is bug-free in general.
"""

import requests
import time
import uuid
import json
import sys

BASE_URL = "http://localhost:8001"
TIMEOUT = 20

RESULTS = []  # (test_name, passed: bool, detail: str)


def record(name, passed, detail=""):
    RESULTS.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def chat(user_id, message, session_id=None, is_session_start=False):
    payload = {
        "user_id": user_id,
        "message": message,
        "is_session_start": is_session_start,
    }
    if session_id:
        payload["session_id"] = session_id
    resp = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=TIMEOUT)
    return resp


# ---------------------------------------------------------------------------
# 1. Health check — and specifically check for the stale-doc mismatch
# ---------------------------------------------------------------------------
def test_health():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        record("health_check", False, "Could not connect — is the server running on :8001?")
        return False

    if r.status_code != 200:
        record("health_check", False, f"HTTP {r.status_code}")
        return False

    data = r.json()
    services = data.get("services", {})
    record("health_check_reachable", True, json.dumps(data))

    # Doc claims Gemini is now the secondary fallback — check /health actually reports it
    has_gemini_key = any("gemini" in str(k).lower() for k in services.keys())
    record(
        "health_reports_gemini_status",
        has_gemini_key,
        "‼️  /health does not mention Gemini — matches the stale example in the doc. "
        "You have no visibility into whether the secondary fallback is actually configured."
        if not has_gemini_key else "Gemini status visible in health check",
    )
    return True


# ---------------------------------------------------------------------------
# 2. Intent coverage — all 10 intents, does the classifier land correctly?
# ---------------------------------------------------------------------------
INTENT_TEST_CASES = [
    ("BALANCE_OVERVIEW", "How am I doing this month?"),
    ("SPENDING_QUERY", "How much did I spend on food this month?"),
    ("BUDGET_STATUS", "Am I over budget?"),
    ("GOAL_PROGRESS", "How close am I to my vacation goal?"),
    ("ANOMALY_ALERT", "Anything unusual in my spending?"),
    ("ADVICE_REQUEST", "Any tips to save more?"),
    ("COMPARISON_QUERY", "How does this month compare to last month?"),
    ("TREND_ANALYSIS", "Is my spending trend improving?"),
    ("GENERAL_CHAT", "hi there"),
    ("OUT_OF_SCOPE", "What's the weather like today?"),
]


def test_intent_coverage(user_id="user_priya"):
    for expected_intent, message in INTENT_TEST_CASES:
        try:
            r = chat(user_id, message)
        except requests.exceptions.ConnectionError:
            record(f"intent::{expected_intent}", False, "connection error")
            continue
        if r.status_code != 200:
            record(f"intent::{expected_intent}", False, f"HTTP {r.status_code}: {r.text[:200]}")
            continue
        data = r.json()
        actual_intent = data.get("intent")
        record(
            f"intent::{expected_intent}",
            actual_intent == expected_intent,
            f"message={message!r} -> got {actual_intent!r}",
        )


# ---------------------------------------------------------------------------
# 3. THE key regression test: transaction-logging attempts must
#    (a) route to OUT_OF_SCOPE and
#    (b) NEVER contain false-confirmation language in the actual text
# ---------------------------------------------------------------------------
FALSE_CONFIRMATION_PHRASES = [
    "added to your", "has been added", "successfully logged", "logged it",
    "saved to your", "done!", "recorded your", "transaction added",
    "added ₹", "logged ₹", "i've added", "i've logged",
]

TRANSACTION_ATTEMPT_MESSAGES = [
    "I spent ₹500 at Zomato",
    "Add 5000 to my vacation fund",
    "I paid 1200 for groceries at Blinkit",
    "log a 300 rupee Uber ride",
]


def test_no_false_confirmation(user_id="user_priya"):
    for msg in TRANSACTION_ATTEMPT_MESSAGES:
        try:
            r = chat(user_id, msg)
        except requests.exceptions.ConnectionError:
            record(f"no_false_confirm::{msg}", False, "connection error")
            continue
        if r.status_code != 200:
            record(f"no_false_confirm::{msg}", False, f"HTTP {r.status_code}")
            continue
        data = r.json()
        text_lower = data.get("text", "").lower()
        intent = data.get("intent")

        # Check intent routing
        record(
            f"routes_to_out_of_scope::{msg}",
            intent == "OUT_OF_SCOPE",
            f"got intent={intent!r} (doc claims all transaction mentions -> OUT_OF_SCOPE)",
        )

        # Check the actual generated text for false confirmation language
        # This is the critical check — intent label alone doesn't guarantee honest text
        found_bad_phrase = next((p for p in FALSE_CONFIRMATION_PHRASES if p in text_lower), None)
        record(
            f"no_false_confirmation_text::{msg}",
            found_bad_phrase is None,
            f'response text contained "{found_bad_phrase}" — bot may still be implying it wrote data'
            if found_bad_phrase else f"response: {data.get('text', '')[:150]!r}",
        )


# ---------------------------------------------------------------------------
# 4. Cache correctness — the specific bug we caught in v2.0
#    Same intent, different slots, within the 5-min window -> must NOT
#    return identical cached answers
# ---------------------------------------------------------------------------
def test_cache_correctness_spending_query(user_id="user_meera"):
    session_id = str(uuid.uuid4())
    r1 = chat(user_id, "How much did I spend on food this month?", session_id=session_id)
    r2 = chat(user_id, "How much did I spend on transport this month?", session_id=session_id)

    if r1.status_code != 200 or r2.status_code != 200:
        record("cache_correctness_spending_query", False, "HTTP error on one of the calls")
        return

    text1 = r1.json().get("text", "")
    text2 = r2.json().get("text", "")

    record(
        "cache_correctness_spending_query",
        text1 != text2,
        "food vs transport queries returned IDENTICAL text within cache window — "
        "cache bug may still be present"
        if text1 == text2 else "Distinct answers returned for distinct categories — as expected",
    )


def test_cache_correctness_comparison_query(user_id="user_meera"):
    session_id = str(uuid.uuid4())
    r1 = chat(user_id, "This month vs last month?", session_id=session_id)
    time.sleep(1)
    r2 = chat(user_id, "This month vs last month?", session_id=session_id)
    # Same question twice is fine to be identical — this just confirms
    # COMPARISON_QUERY isn't erroring out due to being excluded from cache
    ok = r1.status_code == 200 and r2.status_code == 200
    record("comparison_query_not_broken_by_cache_exclusion", ok,
           f"status codes: {r1.status_code}, {r2.status_code}")


# ---------------------------------------------------------------------------
# 5. Auth dev-mode sanity — confirm AUTH_ENABLED=false actually behaves
#    as documented (no header required). If this unexpectedly 401s,
#    someone flipped the flag without telling you.
# ---------------------------------------------------------------------------
def test_auth_dev_mode_no_header():
    r = requests.post(
        f"{BASE_URL}/api/chat",
        json={"user_id": "user_priya", "message": "hi"},
        timeout=TIMEOUT,
    )
    record(
        "auth_dev_mode_accepts_no_header",
        r.status_code == 200,
        f"got HTTP {r.status_code} — if 401, AUTH_ENABLED may have been flipped to true "
        "without JWT_SECRET_KEY being synced, which would break the whole chatbot for the cohort",
    )


# ---------------------------------------------------------------------------
# 6. Rate limiting — 20 req/min/user per the doc. Fire enough to trigger it.
# ---------------------------------------------------------------------------
def test_rate_limit(user_id="user_arjun"):
    statuses = []
    for i in range(25):
        try:
            r = chat(user_id, f"hi {i}")
            statuses.append(r.status_code)
        except requests.exceptions.ConnectionError:
            statuses.append(-1)
    hit_429 = 429 in statuses
    record(
        "rate_limit_triggers_gracefully",
        hit_429,
        f"status codes seen: {set(statuses)} — expected at least one 429 after 20 req/min"
        if not hit_429 else "429 observed as expected after threshold",
    )


# ---------------------------------------------------------------------------
# 7. Session history persistence
# ---------------------------------------------------------------------------
def test_session_persistence(user_id="user_priya"):
    session_id = str(uuid.uuid4())
    chat(user_id, "How am I doing this month?", session_id=session_id, is_session_start=True)
    chat(user_id, "What about my goals?", session_id=session_id)

    r = requests.get(
        f"{BASE_URL}/api/chat/history/{user_id}",
        params={"session_id": session_id},
        timeout=TIMEOUT,
    )
    ok = r.status_code == 200 and len(r.json()) >= 2 if r.status_code == 200 else False
    record("session_history_persists", ok, f"HTTP {r.status_code}, body: {r.text[:200]}")


# ---------------------------------------------------------------------------
# 8. Feedback + preference learning loop
# ---------------------------------------------------------------------------
def test_feedback_loop(user_id="user_arjun"):
    r_chat = chat(user_id, "How much did I spend on food?")
    if r_chat.status_code != 200:
        record("feedback_loop", False, "chat call failed, cannot test feedback")
        return

    session_id = r_chat.json().get("session_id")
    fb_payload = {
        "user_id": user_id,
        "session_id": session_id,
        "message_id": str(uuid.uuid4()),
        "rating": "down",
        "correction": "that category was wrong, it was transport not food",
        "intent": "SPENDING_QUERY",
    }
    r_fb = requests.post(f"{BASE_URL}/api/chat/feedback", json=fb_payload, timeout=TIMEOUT)
    record("feedback_submission", r_fb.status_code == 200, f"HTTP {r_fb.status_code}")

    r_prefs = requests.get(f"{BASE_URL}/api/chat/preferences/{user_id}", timeout=TIMEOUT)
    if r_prefs.status_code == 200:
        corrections = r_prefs.json().get("corrections", [])
        record(
            "correction_stored_in_preferences",
            any("transport" in c.lower() for c in corrections),
            f"corrections list: {corrections}",
        )
    else:
        record("correction_stored_in_preferences", False, f"HTTP {r_prefs.status_code}")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Testing Dekho chatbot at {BASE_URL}\n" + "=" * 60)

    if not test_health():
        print("\nServer unreachable — fix connectivity before running further tests.")
        sys.exit(1)

    print("\n-- Intent coverage --")
    test_intent_coverage()

    print("\n-- Critical: false confirmation regression check --")
    test_no_false_confirmation()

    print("\n-- Cache correctness --")
    test_cache_correctness_spending_query()
    test_cache_correctness_comparison_query()

    print("\n-- Auth dev-mode sanity --")
    test_auth_dev_mode_no_header()

    print("\n-- Rate limiting --")
    test_rate_limit()

    print("\n-- Session persistence --")
    test_session_persistence()

    print("\n-- Feedback loop --")
    test_feedback_loop()

    print("\n" + "=" * 60)
    passed = sum(1 for _, p, _ in RESULTS if p)
    total = len(RESULTS)
    print(f"RESULT: {passed}/{total} checks passed")
    failed = [(n, d) for n, p, d in RESULTS if not p]
    if failed:
        print("\nFAILED CHECKS:")
        for name, detail in failed:
            print(f"  - {name}: {detail}")
        sys.exit(1)
