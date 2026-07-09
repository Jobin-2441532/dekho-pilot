from typing import Any
import asyncpg
from app.config import settings
from app.models.schemas import (
    UserProfile, MonthlySnapshot, BudgetEntry, SavingsGoal, Transaction, Anomaly
)
from datetime import date, timedelta, datetime
import logging

logger = logging.getLogger("dekho.data_layer")

from app.services.db_pool import get_pool

class DataLayer:
    def __init__(self):
        self.conn = None
        self.ctx = None

    def _uid(self, user_id: str) -> int:
        import re
        m = re.search(r'\d+', str(user_id))
        return int(m.group()) if m else 1

    async def __aenter__(self):
        pool = get_pool()
        self.ctx = pool.acquire()
        self.conn = await self.ctx.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.ctx:
            await self.ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def ping(self):
        await self.conn.fetchval("SELECT 1")

    async def get_user_profile(self, user_id: str) -> UserProfile:
        row = await self.conn.fetchrow(
            "SELECT id, name, monthly_budget FROM users WHERE id = $1", 
            self._uid(user_id)
        )
        if not row:
            return UserProfile(
                id=str(user_id),
                name="User",
                primary_goal="save",
                tone_preference="friendly"
            )
        return UserProfile(
            id=str(row["id"]),
            name=row["name"],
            primary_goal="save",
            tone_preference="friendly"
        )

    async def get_monthly_snapshot(self, user_id: str) -> MonthlySnapshot:
        now = date.today()
        first_day = now.replace(day=1)
        
        # In the main database schema, expenses are direction = 'debit' and income is direction = 'credit'
        rows = await self.conn.fetch(
            "SELECT category, sum(amount) as total FROM transactions WHERE user_id = $1 AND direction = 'debit' AND date >= $2 GROUP BY category",
            self._uid(user_id), str(first_day)
        )
        
        by_category = {row["category"]: float(row["total"]) for row in rows if row["category"]}
        total_expenses = sum(by_category.values())
        
        return MonthlySnapshot(
            user_id=user_id,
            month=now.strftime("%Y-%m"),
            total_expenses=total_expenses,
            by_category=by_category
        )

    async def get_monthly_snapshots(self, user_id: str, limit_months: int = 6) -> list[MonthlySnapshot]:
        rows = await self.conn.fetch(
            "SELECT category, amount, date, direction FROM transactions WHERE user_id = $1 ORDER BY date DESC",
            self._uid(user_id)
        )
        
        months_data = {}
        for r in rows:
            if not r["date"]:
                continue
            m = r["date"][:7] # YYYY-MM
            if m not in months_data:
                months_data[m] = {"expenses": 0.0, "by_category": {}}
            
            amt = float(r["amount"] or 0)
            if r["direction"] == "debit":
                months_data[m]["expenses"] += amt
                cat = r["category"] or "Others"
                months_data[m]["by_category"][cat] = months_data[m]["by_category"].get(cat, 0.0) + amt
        
        snapshots = []
        for m, data in sorted(months_data.items(), key=lambda x: x[0], reverse=True)[:limit_months]:
            snapshots.append(MonthlySnapshot(
                user_id=user_id,
                month=m,
                total_expenses=data["expenses"],
                by_category=data["by_category"]
            ))
        return snapshots

    async def get_budget_status(self, user_id: str) -> list[BudgetEntry]:
        budgets_rows = await self.conn.fetch(
            "SELECT category, monthly_limit FROM budgets WHERE user_id = $1",
            self._uid(user_id)
        )
        
        now = datetime.now()
        month_prefix = now.strftime("%Y-%m")
        spent_rows = await self.conn.fetch(
            "SELECT category, SUM(amount) as spent FROM transactions WHERE user_id = $1 AND direction = 'debit' AND date LIKE $2 GROUP BY category",
            self._uid(user_id), f"{month_prefix}%"
        )
        
        spent_map = {}
        for r in spent_rows:
            if r["category"]:
                cat_name = r["category"].split("|")[0].strip()
                spent_map[cat_name] = float(r["spent"] or 0)
                
        budgets = []
        for r in budgets_rows:
            cat_raw = r["category"]
            cat_name = cat_raw.split("|")[0].strip()
            limit = float(r["monthly_limit"] or 0)
            spent = spent_map.get(cat_name, 0.0)
            pct = (spent / limit * 100) if limit > 0 else 0
            budgets.append(BudgetEntry(
                category=cat_raw,
                monthly_limit=limit,
                spent=spent,
                pct_used=round(pct, 1)
            ))
        return budgets

    async def get_goals(self, user_id: str) -> list[SavingsGoal]:
        rows = await self.conn.fetch(
            "SELECT id, name, target_amount, current_amount FROM savings_goals WHERE user_id = $1",
            self._uid(user_id)
        )
        return [
            SavingsGoal(
                id=str(r["id"]),
                goal_name=r["name"],
                target_amount=float(r["target_amount"] or 0),
                current_amount=float(r["current_amount"] or 0)
            ) for r in rows
        ]

    async def get_top_expenses(self, user_id: str, limit: int = 5) -> list[Transaction]:
        now = date.today()
        first_day = now.replace(day=1).isoformat()
        rows = await self.conn.fetch(
            "SELECT id, amount, category, date, direction as type, merchant FROM transactions WHERE user_id = $1 AND direction = 'debit' AND date >= $2 ORDER BY amount DESC LIMIT $3",
            self._uid(user_id), first_day, limit
        )
        return [
            Transaction(
                id=str(r["id"]),
                user_id=user_id,
                amount=float(r["amount"]),
                type="expense",
                category=r["category"] or "Others",
                description=r["merchant"] or r["category"] or "Others",
                date=r["date"][:10] if r["date"] else date.today().isoformat()
            ) for r in rows
        ]

    async def get_recent_transactions(self, user_id: str, days: int = 7, limit: int = 10) -> list[Transaction]:
        start_date = (date.today() - timedelta(days=days)).isoformat()
        rows = await self.conn.fetch(
            "SELECT id, amount, category, date, direction as type, merchant FROM transactions WHERE user_id = $1 AND date >= $2 ORDER BY date DESC LIMIT $3",
            self._uid(user_id), start_date, limit
        )
        return [
            Transaction(
                id=str(r["id"]),
                user_id=user_id,
                amount=float(r["amount"]),
                type="expense",
                category=r["category"] or "Others",
                description=r["merchant"] or r["category"] or "Others",
                date=r["date"][:10] if r["date"] else date.today().isoformat()
            ) for r in rows
        ]

    async def get_anomalies(self, user_id: str, threshold_pct: float = 120.0) -> list[Anomaly]:
        return []

    async def get_user_stats(self, user_id: str) -> dict[str, Any]:
        stats = {}
        start_date = (date.today() - timedelta(days=30)).isoformat()
        rows = await self.conn.fetch(
            "SELECT amount, date FROM transactions WHERE user_id = $1 AND direction = 'debit' AND date >= $2",
            self._uid(user_id), start_date
        )
        if not rows:
            return stats
            
        total_spend = sum(float(r["amount"] or 0) for r in rows)
        unique_days = len(set(r["date"][:10] for r in rows if r["date"])) or 1
        stats["avg_per_day_last_30_days"] = round(total_spend / 30, 2) # Avg over the whole month
        stats["avg_daily_spend_on_active_days"] = round(total_spend / unique_days, 2)
        
        weekend_spend = 0
        weekday_spend = 0
        from datetime import datetime
        for r in rows:
            if not r["date"]: continue
            try:
                dt = datetime.fromisoformat(r["date"][:10])
                if dt.weekday() >= 5:
                    weekend_spend += float(r["amount"] or 0)
                else:
                    weekday_spend += float(r["amount"] or 0)
            except ValueError:
                pass
        
        stats["avg_weekend_spend_last_30_days"] = round(weekend_spend / 8, 2) if weekend_spend else 0
        stats["avg_weekday_spend_last_30_days"] = round(weekday_spend / 22, 2) if weekday_spend else 0
        stats["total_weekend_spend_last_30_days"] = round(weekend_spend, 2)
        stats["total_weekday_spend_last_30_days"] = round(weekday_spend, 2)
        
        return stats
