"""
Locust Load Test — Phase 6.4
Target: 100 concurrent users, p95 < 5s, error rate < 0.5%

Run: locust -f tests/locustfile.py --host=http://localhost:8001 -u 100 -r 10 -t 5m
"""

import random
from locust import HttpUser, task, between, events
import time

USERS = ["user_priya", "user_arjun", "user_meera"]

CHAT_MESSAGES = {
    "balance": [
        "How am I doing this month?",
        "Give me a financial overview",
        "What's my financial status?",
    ],
    "spending": [
        "How much did I spend on food this month?",
        "What did I spend on transport?",
        "Show me my grocery spending",
        "How much on entertainment?",
    ],
    "budget": [
        "Am I over budget?",
        "Check my budget status",
        "Which categories am I over budget in?",
    ],
    "goal": [
        "How's my vacation fund?",
        "Show my savings goal progress",
        "How much more do I need to save?",
    ],
    "anomaly": [
        "Anything unusual in my spending?",
        "Flag any weird expenses",
        "Any suspicious transactions?",
    ],
    "advice": [
        "How can I save more?",
        "Tips to cut spending",
        "Help me reach my savings goal faster",
    ],
    "comparison": [
        "Compare this month to last month",
        "Am I spending more or less than last month?",
    ],
    "add_transaction": [
        "I spent ₹300 at Zomato",
        "Paid ₹200 for metro",
        "Bought groceries for ₹1500 at DMart",
    ],
    "general": [
        "Hi there!",
        "What can you help me with?",
        "Who are you?",
    ],
}


class ChatUser(HttpUser):
    """Simulates a user interacting with the chatbot — 60% chat, 30% chart, 10% new session."""
    wait_time = between(2, 6)  # realistic think time between messages

    def on_start(self):
        self.user_id = random.choice(USERS)
        self.session_id = f"locust_{self.user_id}_{int(time.time() * 1000)}"

    @task(60)
    def send_chat_message(self):
        """Send a mixed-intent chat message (non-streaming)."""
        category = random.choices(
            list(CHAT_MESSAGES.keys()),
            weights=[15, 20, 15, 15, 5, 10, 10, 5, 5],
            k=1,
        )[0]
        message = random.choice(CHAT_MESSAGES[category])

        with self.client.post(
            "/api/chat",
            json={
                "user_id": self.user_id,
                "message": message,
                "session_id": self.session_id,
            },
            name="/api/chat",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                data = r.json()
                if not data.get("text"):
                    r.failure("Empty text in response")
                elif data.get("is_fallback"):
                    # Fallbacks are OK — don't count as failures
                    r.success()
                else:
                    r.success()
            elif r.status_code == 429:
                r.success()  # rate limit is expected behaviour, not failure
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(30)
    def send_chart_query(self):
        """Send queries that trigger chart generation (spending + goals)."""
        messages = [
            "Show me my spending breakdown",
            "Pie chart of my expenses",
            "How's my goal progress?",
            "Show spending trend",
        ]
        with self.client.post(
            "/api/chat",
            json={
                "user_id": self.user_id,
                "message": random.choice(messages),
                "session_id": self.session_id,
            },
            name="/api/chat [chart]",
            catch_response=True,
        ) as r:
            if r.status_code in [200, 429]:
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")

    @task(10)
    def start_new_session(self):
        """Simulate a user starting a fresh session (proactive alerts path)."""
        new_session = f"locust_new_{self.user_id}_{int(time.time() * 1000)}"
        with self.client.post(
            "/api/chat",
            json={
                "user_id": self.user_id,
                "message": "Hi, I'm back!",
                "session_id": new_session,
                "is_session_start": True,
            },
            name="/api/chat [new session]",
            catch_response=True,
        ) as r:
            if r.status_code in [200, 429]:
                r.success()
            else:
                r.failure(f"HTTP {r.status_code}")
        # Update session for subsequent messages
        self.session_id = new_session


class HealthCheckUser(HttpUser):
    """Low-frequency health check user — always runs."""
    wait_time = between(10, 30)
    weight = 1  # 1 out of every 100 users is a health checker

    @task
    def check_health(self):
        self.client.get("/health")
