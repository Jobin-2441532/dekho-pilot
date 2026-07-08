import random
from datetime import datetime, date
from app.services.insight_engine_v2 import UserData, SpendingPattern, EmotionalTrigger, pick, fmt

def get_time_of_day_greeting():
    hour = datetime.now().hour
    if 6 <= hour < 11:
        return "morning"
    elif 11 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def get_hero_card_mode(d: UserData, last_hero_mode: str = None, last_mode_d_date: date = None) -> dict:
    """
    Implements the 5-step Master Decision Tree for the Hero Card.
    Returns a dict with: mode, greeting, headline, subtext, breakdown_type, mode_d_question (optional).
    """
    time_greeting = get_time_of_day_greeting()
    greeting = f"Good {time_greeting}, {d.name}."

    # Step 1: Zero Spend Check
    if d.today_spend == 0:
        return mode_quiet_day(d, greeting)

    # Step 2: Milestone Check (Mode E)
    if d.streak_days in [3, 7, 14, 30] and last_hero_mode != "Mode E":
        return mode_e_milestone(d, greeting)
    if d.savings_milestone_hit and last_hero_mode != "Mode E":
        return mode_e_milestone(d, greeting)

    # Step 2: Data Sufficiency Check
    if d.days_on_app < 14:
        # Fallback to Mode C or early onboarding A
        if last_hero_mode != "Mode C":
            return mode_c_forecast(d, greeting)

    # Step 3: Dominant Pattern Check (Mode A)
    # If a strong behavioral pattern is detected, surface it.
    if d.primary_pattern in [SpendingPattern.COMFORT_SPENDING, SpendingPattern.IMPULSE_HEAVY, SpendingPattern.CELEBRATION_SPENDING, SpendingPattern.SOCIAL_SPENDING]:
        if last_hero_mode != "Mode A":
            return mode_a_daily_character(d, greeting)

    # Step 4: Selection (If nothing else fired, pick B or C or fallback A)
    pool = ["Mode A", "Mode B", "Mode C"]
    if last_hero_mode in pool:
        pool.remove(last_hero_mode)
    
    selected_mode = random.choice(pool)
    if selected_mode == "Mode A":
        return mode_a_daily_character(d, greeting)
    elif selected_mode == "Mode B":
        return mode_b_unexpected(d, greeting)
    else:
        return mode_c_forecast(d, greeting)

def mode_a_daily_character(d: UserData, greeting: str) -> dict:
    top_cat = d.today_top_category or "spending"
    headline = "Today had a comfort flavour."
    subtext = f"You spent a little more on {top_cat}. That's a human response to a long day."
    
    if d.primary_pattern == SpendingPattern.SOCIAL_SPENDING:
        headline = "Social energy drove spending today."
        subtext = f"People time usually comes with some spending — {top_cat} was the focus."
    elif d.primary_pattern == SpendingPattern.INTENTIONAL:
        headline = "A clean, intentional day."
        subtext = f"Most of today's spending was planned, especially on {top_cat}. You are building strong habits."
    
    # Calculate a dynamic direction word based on percentage
    direction = "higher" if d.week_vs_last_week_pct >= 0 else "lower"
    pct_val = abs(d.week_vs_last_week_pct)
    
    return {
        "mode": "Mode A",
        "greeting": greeting,
        "headline": headline,
        "subtext": subtext,
        "breakdown_type": "The Why",
        "breakdown_data": {
            "title": "Why we're saying this",
            "points": [
                f"{fmt(d.today_top_amount)} went to {top_cat}.",
                f"This is {pct_val}% {direction} than last week." if pct_val > 0 else "This is consistent with your recent pace.",
                f"Pattern detected: {d.primary_pattern.value.replace('_', ' ').title()}."
            ]
        }
    }

def mode_b_unexpected(d: UserData, greeting: str) -> dict:
    top_cat = d.today_top_category or "Recent spending"
    direction = "up" if d.week_vs_last_week_pct >= 0 else "down"
    pct_val = abs(d.week_vs_last_week_pct)
    
    headline = f"{top_cat} is {direction} {pct_val}% this week."
    subtext = f"You've spent a bit differently on {top_cat} lately. Just an observation, no judgement."
    
    last_week_est = d.week_spend / (1 + (d.week_vs_last_week_pct/100.0)) if d.week_vs_last_week_pct != 0 and d.week_vs_last_week_pct != -100 else 0
    
    return {
        "mode": "Mode B",
        "greeting": greeting,
        "headline": headline,
        "subtext": subtext,
        "breakdown_type": "Personal Pattern",
        "breakdown_data": {
            "title": f"Your {top_cat} Pattern",
            "points": [
                f"Last week's pace: {fmt(last_week_est)}",
                f"This week's pace: {fmt(d.week_spend)}",
                "Often spikes towards the end of the week."
            ]
        }
    }

def mode_c_forecast(d: UserData, greeting: str) -> dict:
    day_name = datetime.now().strftime("%A")
    headline = f"Approaching {day_name}."
    
    status = "You're on track to meet your monthly goal." if d.remaining_budget >= 0 else "You've exceeded your monthly budget."
    
    subtext = f"You have {fmt(d.remaining_budget)} left for the month. Enjoy the day, intentionally."
    return {
        "mode": "Mode C",
        "greeting": greeting,
        "headline": headline,
        "subtext": subtext,
        "breakdown_type": "Forward-Looking",
        "breakdown_data": {
            "title": "Looking Ahead",
            "points": [
                f"Remaining budget: {fmt(d.remaining_budget)}",
                f"Current average pace: {fmt(d.avg_daily_spend)}/day",
                status
            ]
        }
    }

def mode_quiet_day(d: UserData, greeting: str) -> dict:
    headline = "A quiet day for your wallet."
    subtext = "Barely anything went out today. Rest days matter."
    return {
        "mode": "Mode Quiet",
        "greeting": greeting,
        "headline": headline,
        "subtext": subtext,
        "breakdown_type": "The Why",
        "breakdown_data": {
            "title": "Why we're saying this",
            "points": [
                "₹0 spent today.",
                "Not every day needs a transaction.",
                "You are maintaining financial discipline."
            ]
        }
    }

def mode_e_milestone(d: UserData, greeting: str) -> dict:
    headline = f"🔥 {d.streak_days} days running."
    subtext = "Dekho is learning your habits. Consistency is how wealth is built."
    return {
        "mode": "Mode E",
        "greeting": greeting,
        "headline": headline,
        "subtext": subtext,
        "breakdown_type": "Emotional Context",
        "breakdown_data": {
            "title": "The Power of Consistency",
            "points": [
                f"You've checked in {d.streak_days} days in a row.",
                "People who check in daily save 23% more on average.",
                "Keep the momentum going."
            ]
        }
    }
