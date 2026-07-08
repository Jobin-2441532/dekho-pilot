import os
import json
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.notification import Notification, PushSubscription
from app.models.transaction import Transaction
from app.models.financial import Budget
from pywebpush import webpush, WebPushException
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

def send_web_push(subscription: PushSubscription, payload: dict):
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth
                }
            },
            data=json.dumps(payload),
            vapid_private_key=os.getenv("VAPID_PRIVATE_KEY"),
            vapid_claims={
                "sub": os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@dekho.app")
            }
        )
    except WebPushException as ex:
        print("Web Push Failed:", ex)
        if ex.response and ex.response.status_code == 410:
            # Subscription expired or unsubscribed, should delete
            with SessionLocal() as db:
                db.delete(subscription)
                db.commit()

def dispatch_notification(db: Session, user: User, rule_type: str, title: str, message: str):
    # Check limit of 3 per day
    today = date.today()
    count_today = db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.created_at >= today
    ).count()

    if count_today >= 3:
        return # Skip if already sent 3 today

    # Create DB record
    n = Notification(
        user_id=user.id,
        rule_type=rule_type,
        title=title,
        message=message
    )
    db.add(n)
    db.commit()

    # Send Web Push
    subs = db.query(PushSubscription).filter(PushSubscription.user_id == user.id).all()
    for sub in subs:
        send_web_push(sub, {
            "title": title,
            "body": message,
            "url": "/"
        })

def evaluate_morning_rules():
    with SessionLocal() as db:
        users = db.query(User).all()
        for u in users:
            if datetime.now().weekday() == 0:
                budgets = db.query(Budget).filter(Budget.user_id == u.id).all()
                for b in budgets:
                    if b.spent_amount >= (b.amount / 2):
                        dispatch_notification(db, u, "budget_checkin", "Budget Update", f"You're about halfway through your {b.category} budget - here's how it's shaping up.")
                        break

def evaluate_afternoon_rules():
    with SessionLocal() as db:
        users = db.query(User).all()
        for u in users:
            tx_today = db.query(Transaction).filter(
                Transaction.user_id == u.id,
                Transaction.date == date.today()
            ).count()
            
            if tx_today > 0:
                dispatch_notification(db, u, "daily_reflection", "Daily Reflection", "Today had a balanced flavour - see what shaped it.")

def evaluate_night_rules():
    with SessionLocal() as db:
        users = db.query(User).all()
        today_date = date.today()
        
        for u in users:
            tx_today = db.query(Transaction).filter(
                Transaction.user_id == u.id,
                Transaction.date == today_date
            ).count()

            if tx_today == 0:
                dispatch_notification(db, u, "log_nudge", "End of Day", "A quiet page today \u2014 anything to add before the day closes?")
            elif getattr(u, 'current_streak_days', 0) >= 2 and getattr(u, 'last_checkin_date', None) != today_date:
                dispatch_notification(db, u, "streak_at_risk", "Streak At Risk", f"Your streak's at {u.current_streak_days} \u2014 a quick log keeps it going.")

            if datetime.now().weekday() == 4:
                dispatch_notification(db, u, "weekend_pattern", "Weekend Ready", "Weekends have tended to look a little different for you - worth a glance before this one starts.")

            total_tx = db.query(Transaction).filter(Transaction.user_id == u.id).count()
            if total_tx > 0 and total_tx % 10 == 0:
                dispatch_notification(db, u, "milestone", "Milestone Reached", f"That's {total_tx} spends logged - a real picture is starting to form.")

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=timezone('Asia/Kolkata'))
    # Morning: 9:00 AM
    scheduler.add_job(evaluate_morning_rules, 'cron', hour=9, minute=0)
    # Afternoon: 2:00 PM
    scheduler.add_job(evaluate_afternoon_rules, 'cron', hour=14, minute=0)
    # Night: 9:00 PM
    scheduler.add_job(evaluate_night_rules, 'cron', hour=21, minute=0)
    
    scheduler.start()
    return scheduler
