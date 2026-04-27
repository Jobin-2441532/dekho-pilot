"""
SMS Parser — regex-based extraction of transactions from Indian bank SMS alerts.
Covers HDFC, SBI, ICICI, Axis, Kotak, and generic UPI formats.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

ParsedRow = Dict[str, Any]

# ---------------------------------------------------------------------------
# Regex patterns for common Indian bank SMS formats
# ---------------------------------------------------------------------------
PATTERNS = [
    # HDFC: "Rs.500.00 debited from a/c ...1234 on 27-04-26 to SWIGGY. Avl Bal..."
    {
        "regex": r"(?:rs\.?|inr\.?|₹)\s*([\d,]+\.?\d*)\s+debited\s+(?:from\s+(?:a/c|ac|acct|account)[^o]*)?\s*(?:on\s+([\d\-/]+))?\s*(?:to\s+([^\.\n,]+))?",
        "direction": "debit",
    },
    # HDFC credit: "Rs.500.00 credited to a/c ...1234 on 27-04-26"
    {
        "regex": r"(?:rs\.?|inr\.?|₹)\s*([\d,]+\.?\d*)\s+credited\s+(?:to\s+(?:a/c|ac|acct|account)[^o]*)?\s*(?:on\s+([\d\-/]+))?\s*(?:by\s+([^\.\n,]+))?",
        "direction": "credit",
    },
    # SBI/ICICI: "INR 1,500.00 debited from SBI A/c XXXX1234 on 27Apr26"
    {
        "regex": r"(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+(?:has been\s+)?debited\s+from\s+\w+\s+a/c[^o]*?(?:on\s+([\d\w\-/]+))?\s*(?:at|to|for)\s+([^\.\n,]+)",
        "direction": "debit",
    },
    # SBI credit variant
    {
        "regex": r"(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+(?:has been\s+)?credited\s+(?:to\s+\w+\s+a/c[^o]*)?\s*(?:on\s+([\d\w\-/]+))?\s*(?:by|from)\s+([^\.\n,]+)",
        "direction": "credit",
    },
    # Generic UPI debit: "UPI payment of Rs 250 to ZOMATO@YESBANK ref 123..."
    {
        "regex": r"upi\s+(?:payment|txn)\s+of\s+(?:rs\.?|inr\.?|₹)\s*([\d,]+\.?\d*)\s+to\s+([^\s]+)\s+(?:on\s+([\d\-/]+))?",
        "direction": "debit",
        "merchant_group": 2,
        "date_group": 3,
        "amount_group": 1,
    },
    # Generic UPI credit
    {
        "regex": r"(?:rs\.?|inr\.?|₹)\s*([\d,]+\.?\d*)\s+received\s+(?:via\s+upi\s+)?from\s+([^\s\n]+)\s+(?:on\s+([\d\-/]+))?",
        "direction": "credit",
        "merchant_group": 2,
        "date_group": 3,
        "amount_group": 1,
    },
    # Axis/Kotak: "Debit of INR 500 from Ac ...1234 on 27-04-2026 SWIGGY"
    {
        "regex": r"(?:debit|dr)\s+of\s+(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+from\s+ac[^\d]*[\d]+\s+on\s+([\d\-/]+)\s+([^\n\.]+)",
        "direction": "debit",
    },
    # Kotak credit
    {
        "regex": r"(?:credit|cr)\s+of\s+(?:inr|rs\.?|₹)\s*([\d,]+\.?\d*)\s+(?:to|in)\s+ac[^\d]*[\d]+\s+on\s+([\d\-/]+)\s+([^\n\.]+)",
        "direction": "credit",
    },
]

DATE_FORMATS = [
    "%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y",
    "%d%b%y", "%d%b%Y", "%d-%b-%Y", "%d-%b-%y",
    "%d %b %Y", "%d %b %y",
]


def _parse_amount(raw: str) -> float:
    cleaned = re.sub(r"[,\s]", "", raw)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _parse_date(raw: Optional[str]) -> str:
    if not raw:
        return datetime.today().strftime("%Y-%m-%d")
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return datetime.today().strftime("%Y-%m-%d")


def _clean_merchant(raw: Optional[str]) -> str:
    if not raw:
        return "Unknown"
    # Strip UPI handles like @oksbi, @paytm
    cleaned = re.sub(r"@\w+", "", raw).strip()
    # Remove trailing ref numbers
    cleaned = re.sub(r"\s+ref\.?\s*\w+", "", cleaned, flags=re.IGNORECASE).strip()
    # Title-case
    return cleaned.title() or "Unknown"


def parse_sms(text: str) -> Optional[ParsedRow]:
    """
    Parse a single SMS string and return a ParsedRow or None if unrecognised.
    """
    text_lower = text.lower().strip()

    for pattern in PATTERNS:
        match = re.search(pattern["regex"], text_lower, re.IGNORECASE)
        if not match:
            continue

        # Handle patterns with explicit group mappings
        amt_grp = pattern.get("amount_group", 1)
        date_grp = pattern.get("date_group", 2)
        merch_grp = pattern.get("merchant_group", 3)

        try:
            amount = _parse_amount(match.group(amt_grp))
            date_raw = match.group(date_grp) if date_grp <= len(match.groups()) else None
            merchant_raw = match.group(merch_grp) if merch_grp <= len(match.groups()) else None
        except (IndexError, AttributeError):
            continue

        if amount == 0:
            continue

        return {
            "date": _parse_date(date_raw),
            "description": _clean_merchant(merchant_raw),
            "amount": amount,
            "direction": pattern["direction"],
        }

    return None


def parse_sms_block(text: str) -> List[ParsedRow]:
    """
    Parse a block of SMS messages (newline-separated) and return all recognised rows.
    """
    results = []
    # Split by blank lines or common SMS separators
    messages = [m.strip() for m in re.split(r"\n{2,}|---+", text) if m.strip()]

    for msg in messages:
        parsed = parse_sms(msg)
        if parsed:
            results.append(parsed)

    return results
