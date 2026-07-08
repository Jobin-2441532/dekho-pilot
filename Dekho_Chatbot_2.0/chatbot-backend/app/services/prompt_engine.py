"""
Prompt Engine — assembles the final LLM prompt from user context + intent.
Implements the "Dekho" persona and all intent-specific sub-templates.
"""

from __future__ import annotations
import json
from app.models.schemas import UserFinancialContext
from app.services.intent_detector import IntentResult
from app.utils.formatters import fmt_inr, fmt_pct, fmt_days

# ── Master System Prompt ───────────────────────────────────────────────────────

MASTER_SYSTEM_PROMPT = """You are "Dekho" — a warm, curious personal finance companion built for Indian users.

## Your Identity
- Your name is Dekho. You are NOT a human, but you are friendly and approachable.
- You observe, reflect, and offer options — you never tell the user what to do.
- You are genuinely interested in helping users understand their money, not manage it for them.
- Speak naturally as if texting a trusted friend who's good with numbers.
- Use the user's first name occasionally to make it feel personal.
- Use 1-2 relevant emojis per response — never more, never forced.
- Keep responses concise: 2-3 sentences maximum unless the user explicitly asks for more detail.

## Tone — Guidance, Not Advice
- NEVER instruct or direct the user. Instead of "Cut back on shopping", say "Shopping is running a bit high — some people find it easier to set a weekly limit."
- NEVER say "you should", "you must", "you need to", "make sure you". Replace with "one option could be", "you might want to consider", "some people find it helpful to".
- Offer observations and possibilities. The user is in control — they decide what to do.
- If a user asks for advice, frame it as "here are a few things that have worked for others" — not directives.
- End advice-heavy responses with a gentle nudge: "You know your situation best — just sharing what might help 😊"

## Scope — Finance Only
- You ONLY discuss personal finance topics: spending, budgets, savings goals, income, transactions, and financial patterns.
- If asked about anything else (technology, general knowledge, relationships, your own gender/identity, etc.), politely decline and redirect: "I'm only set up to help with your finances — want me to check something about your spending or budget instead?"
- If asked who you are or what you can do: briefly describe your finance capabilities, not your tech stack or backend.
- If asked about other users' data: "I only have access to your personal financial data, not anyone else's."

## Avoiding Repetition
- NEVER repeat information already covered in this conversation — check the Recent Conversation section before answering.
- If the user asks the same question again, acknowledge it and add NEW context or a different angle.
- Do not restate the user's question back to them before answering.

## Language Rules
- ALWAYS use ₹ (not Rs., INR, or R). Format: ₹1,23,456 (Indian number system).
- Never fabricate numbers. Every ₹ figure must come from the provided user context.

## Read-Only Contract (CRITICAL — never break this)
- You CANNOT write to, modify, or delete any user data. You are a read-only companion.
- NEVER use words like "Done!", "Added!", "Saved!", "Recorded!", "Logged!", "Updated!" in any context that implies you changed the user's data.
- If a user asks you to add, log, or delete something: acknowledge what they said, but always remind them to confirm it in their app where the actual change happens.
- Violating this rule destroys user trust — a user who believes their transaction was saved when it wasn't will lose financial data.

## For investment, tax, or insurance questions
- End with "I'm not a SEBI-registered advisor — please consult a financial professional for personalised guidance."


## Response Format
- Plain text only. No markdown headers, no bullet lists unless the user asks for a breakdown.
- One clear insight per response. Use progressive disclosure — offer to go deeper at the end.
- Quick action suggestions are added SEPARATELY (not in your text response).

## Past Conversations (Memory)
{past_summaries}

## User Context
{user_context}

## Recent Conversation
{conversation_history}
"""

# ── Intent-specific sub-prompts ───────────────────────────────────────────────

INTENT_INSTRUCTIONS: dict[str, str] = {
    "BALANCE_OVERVIEW": (
        "Give a 2-sentence financial health summary for this month. "
        "Mention income vs spending and highlight the single most important observation "
        "(e.g. savings rate, biggest overspend category, or goal progress). "
        "Keep it upbeat and factual — not prescriptive. Do not tell the user what to change."
    ),
    "SPENDING_QUERY": (
        "Answer the spending question directly with the exact ₹ figure. "
        "If a budget exists for that category, mention the percentage used as an observation. "
        "One sentence answer + one sentence neutral context. Do not suggest changes."
    ),
    "BUDGET_STATUS": (
        "Report budget health as neutral observations. If categories are over budget, name them with ₹ figures. "
        "Frame overruns as observations: 'Shopping has gone a bit above the limit this month.' "
        "Do not tell the user to cut back — simply present the picture. If all is well, say so warmly."
    ),
    "GOAL_PROGRESS": (
        "Report on the relevant savings goal. State: current amount saved, target, percentage complete, "
        "and days remaining if there's a deadline. Calculate how much per day/week they'd need to save "
        "to hit the goal on time. End with light encouragement — no pressure."
    ),
    "ANOMALY_ALERT": (
        "Point out the unusual spending as a curious observation, not an alarm. "
        "Mention the category, the current amount, and how it compares to their typical spending. "
        "Ask if it was intentional. Keep the tone genuinely curious — 'Noticed something interesting...'"
    ),
    "ADVICE_REQUEST": (
        "Share 2 observations based on the user's ACTUAL spending data, framed as possibilities. "
        "Use language like 'some people find it helpful to...', 'one option could be...', 'you might consider...'. "
        "Reference real categories and ₹ amounts from their context. "
        "End with: 'You know your situation best — just sharing what might help 😊' "
        "Do NOT give generic advice. Be specific to their actual numbers."
    ),
    "COMPARISON_QUERY": (
        "Compare the relevant periods or categories. State the key change in ₹ and percentage as a neutral fact. "
        "Identify the single biggest driver of any increase or decrease. "
        "Keep it to 2 sentences max. No judgment on whether the change is good or bad."
    ),
    "TREND_ANALYSIS": (
        "Describe the spending trend in 2 sentences as a neutral observation. Is it improving, worsening, or stable? "
        "Mention the most significant trend without framing it as a problem. Offer to show a chart if they'd like a visual."
    ),


    "OUT_OF_SCOPE": (
        "Check if the user is trying to log a transaction (e.g. 'I spent ₹500', 'paid 800 for groceries'). "
        "If so, respond: 'I can see you want to log that — tap the + button in the Dekho app to add it. Once it's saved, come back and I can help you understand how it fits into your spending!' "
        "For all other out-of-scope questions: politely let the user know you're only set up to help with their personal finance data. "
        "Do NOT answer the out-of-scope question. Do NOT introduce yourself. "
        "Keep it to 1-2 friendly sentences, then offer a finance-related alternative."
    ),
    "GENERAL_CHAT": (
        "Respond as a warm, friendly companion — but keep it very brief (1-2 sentences max). "
        "ONLY introduce yourself as 'Dekho' if the user is explicitly saying hello/hi for the first time (greetings like 'hi', 'hello', 'hey'). "
        "For casual questions like 'how are you', 'hows life', 'what's up' — respond naturally and briefly WITHOUT introducing yourself. "
        "For 'what can you do' queries, briefly mention you help with spending, budgets, goals and financial patterns. "
        "NEVER repeat the same self-introduction twice in the same conversation. "
        "Do not redirect to finance unless the user clearly wants to change topic."
    ),
}

# ── Quick replies per intent ───────────────────────────────────────────────────

QUICK_REPLIES: dict[str, list[str]] = {
    "BALANCE_OVERVIEW":  ["Show spending breakdown", "Check my budget", "Goal progress"],
    "SPENDING_QUERY":    ["See full breakdown", "Compare to last month", "How does this compare to my budget?"],
    "BUDGET_STATUS":     ["Which categories are over?", "Show spending breakdown", "View my goals"],
    "GOAL_PROGRESS":     ["How much more to save?", "View all goals", "Show my savings rate"],
    "ANOMALY_ALERT":     ["Show me the transactions", "That was intentional", "Show all unusual spending"],
    "ADVICE_REQUEST":    ["Show my top expenses", "Check my budget", "View goal progress"],
    "COMPARISON_QUERY":  ["Show spending trend", "What changed the most?", "See full breakdown"],
    "TREND_ANALYSIS":    ["Show spending breakdown", "Month-by-month view", "Check my budget"],
    "OUT_OF_SCOPE":      ["Show my summary", "Check my budget", "View my goals"],
    "GENERAL_CHAT":      ["Show my summary", "Check my budget", "View my goals"],
}

# ── Chart triggers per intent ─────────────────────────────────────────────────

def should_include_chart(intent: str, slots: dict) -> str | None:
    """Return chart type to include, or None."""
    auto_chart_intents = {
        "BALANCE_OVERVIEW":  "pie",
        "SPENDING_QUERY":    "bar",
        "BUDGET_STATUS":     None,
        "COMPARISON_QUERY":  "bar",
        "TREND_ANALYSIS":    "line",
        "GOAL_PROGRESS":     "progress",
    }
    return auto_chart_intents.get(intent)


# ── Context formatter ─────────────────────────────────────────────────────────

def format_context_for_prompt(ctx: UserFinancialContext) -> str:
    """Render the financial context as a readable block for the LLM."""
    from datetime import datetime
    now = datetime.now()
    curr_month_str = now.strftime("%B %Y")
    
    lines = [
        f"User: {ctx.user.name} | Goal: {ctx.user.primary_goal}",
        f"Current Month ({curr_month_str}): Spent {fmt_inr(ctx.current_month.total_expenses)}",
        "",
        "Spending by category this month:",
    ]
    for cat, amt in sorted(ctx.current_month.by_category.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {cat}: {fmt_inr(amt)}")

    if ctx.historical_months:
        lines.append("")
        lines.append("Historical Spending & Income per Month:")
        curr_m_code = now.strftime("%Y-%m")
        for m in ctx.historical_months:
            if m.month == curr_m_code:
                continue
            try:
                m_dt = datetime.strptime(m.month, "%Y-%m")
                m_name = m_dt.strftime("%B %Y")
            except:
                m_name = m.month
            
            lines.append(f"  - {m_name}: Spent {fmt_inr(m.total_expenses)}")
            for cat, amt in sorted(m.by_category.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"    * {cat}: {fmt_inr(amt)}")

    if ctx.budget_alerts:
        lines.append("")
        lines.append("⚠️ Budget observations:")
        for alert in ctx.budget_alerts:
            lines.append(f"  {alert.category}: {fmt_inr(alert.spent)} of {fmt_inr(alert.limit)} limit ({fmt_pct(alert.pct_used)} used)")

    if ctx.goals:
        lines.append("")
        lines.append("Savings goals:")
        for goal in ctx.goals:
            days_str = f", {fmt_days(goal.days_left)} remaining" if goal.days_left is not None else ""
            lines.append(f"  {goal.goal_name}: {fmt_inr(goal.current_amount)}/{fmt_inr(goal.target_amount)} ({goal.pct_complete}%){days_str}")

    if ctx.anomalies:
        lines.append("")
        lines.append("🔍 Unusual spending observed:")
        for a in ctx.anomalies:
            lines.append(f"  {a.category}: {fmt_inr(a.current_spend)} (typically {fmt_inr(a.avg_3month)}, {a.pct_over_avg}% above average)")

    if ctx.top_expenses:
        lines.append("")
        lines.append("Top expenses this month:")
        for t in ctx.top_expenses[:5]:
            lines.append(f"  {t.description or t.category}: {fmt_inr(t.amount)} on {t.date}")

    if ctx.recent_transactions:
        lines.append("")
        lines.append("Recent transactions (last 7 days):")
        for t in ctx.recent_transactions:
            desc = t.description or t.category or "Others"
            t_type = "expense" if t.type == "expense" else "income"
            lines.append(f"  - {desc}: {fmt_inr(t.amount)} ({t_type}) on {t.date}")

    if ctx.user_stats:
        lines.append("")
        lines.append("Additional Statistics:")
        for k, v in ctx.user_stats.items():
            lines.append(f"  - {k.replace('_', ' ').title()}: {fmt_inr(v) if isinstance(v, (int, float)) else v}")

    return "\n".join(lines)


def format_history_for_prompt(history: list[dict]) -> str:
    """Format conversation history for injection into prompt."""
    if not history:
        return "(No prior conversation this session)"
    lines = []
    for msg in history[-6:]:  # last 3 turns
        role = "User" if msg["role"] == "user" else "Dekho"
        lines.append(f"{role}: {msg['content'][:300]}")
    return "\n".join(lines)


# ── Quick Reply Generator ─────────────────────────────────────────────────────

QUICK_REPLY_SYSTEM_PROMPT = """You generate short follow-up question suggestions for a personal finance chatbot called Dekho.

Dekho ONLY handles personal finance topics: spending, budgets, savings goals, income, transactions, trends.

Given the chatbot's last response, suggest exactly 3 natural follow-up questions the user might ask Dekho next.

CRITICAL Rules:
- Every suggestion MUST be a question Dekho can answer from the user's financial data
- NEVER suggest questions about general knowledge, prices of products, external information, or anything not related to the USER'S OWN finances
- Good: "How does food spending compare to last month?", "Which goal is closest to completion?", "Am I over budget anywhere?"
- BAD: "What's the average cost of a bike?", "What is inflation?", "How do I invest in stocks?"
- Each suggestion must be a complete question or short phrase (max 8 words)
- Make them directly relevant to what was just discussed in the response
- Format: a JSON array of 3 strings ONLY. No markdown, no explanation, no code fences.
- Example output: ["How does this compare to last month?", "Which category is highest?", "Am I on track for my goals?"]
"""


def build_quick_replies_prompt(bot_response: str, intent: str) -> tuple[str, str]:
    """Build (system_prompt, user_message) for the quick-reply LLM call."""
    return (
        QUICK_REPLY_SYSTEM_PROMPT,
        f"Intent: {intent}\n\nDekho's response:\n{bot_response[:500]}\n\nSuggest 3 follow-up questions as a JSON array:",
    )



def build_prompt(
    ctx: UserFinancialContext,
    intent_result: IntentResult,
    history: list[dict],
    past_summaries: list[str] | None = None,
    pref_block: str = "",
) -> tuple[str, str]:
    """
    Build (system_prompt, user_instruction) for the LLM.
    Returns the assembled master system prompt + the intent-specific user turn.
    Optionally injects cross-session memory summaries and learned user preferences.
    """
    context_block = format_context_for_prompt(ctx)
    history_block = format_history_for_prompt(history)

    # Cross-session memory
    if past_summaries:
        summaries_block = "\n".join(f"- {s}" for s in past_summaries)
    else:
        summaries_block = "(No previous sessions)"

    system = MASTER_SYSTEM_PROMPT.format(
        past_summaries=summaries_block,
        user_context=context_block,
        conversation_history=history_block,
    )

    # Append learned user preferences block if available
    if pref_block:
        system = system + "\n\n" + pref_block

    intent_instruction = INTENT_INSTRUCTIONS.get(
        intent_result.intent,
        INTENT_INSTRUCTIONS["GENERAL_CHAT"],
    )

    # Enrich instruction with slots
    slot_str = ""
    if intent_result.slots:
        slot_str = f"\n\nExtracted from user's message: {json.dumps(intent_result.slots)}"

    user_instruction = f"{intent_instruction}{slot_str}"

    return system, user_instruction

