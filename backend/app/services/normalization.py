"""
NormalizationService — converts ParsedRows from any source into canonical
Transaction ORM records in the database.
"""
import re
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from app.models import Transaction

ParsedRow = Dict[str, Any]

# ---------------------------------------------------------------------------
# Keyword-based auto-categorization (pre-ML baseline)
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Food & Dining": [
        "swiggy", "zomato", "uber eats", "dominos", "pizza", "burger", "restaurant",
        "cafe", "food", "dining", "biryani", "mcdonalds", "kfc", "subway", "barbeque",
        "dhaba", "hotel", "bakery", "chaayos", "starbucks", "coffee"
    ],
    "Transport": [
        "uber", "ola", "rapido", "auto", "cab", "taxi", "metro", "irctc", "train",
        "bus", "petrol", "fuel", "fastag", "toll", "bmtc", "dtc", "indigo", "spicejet",
        "air india", "airline", "flight", "parking"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "nykaa", "meesho", "snapdeal",
        "shopping", "mall", "retail", "fashion", "clothes", "apparel", "shoppers stop",
        "lifestyle", "big bazaar", "dmart"
    ],
    "Health & Fitness": [
        "pharmacy", "medical", "hospital", "clinic", "doctor", "chemist",
        "apollo", "medplus", "netmeds", "1mg", "healthkart", "gym", "fitness",
        "cult.fit", "yoga", "diagnostics", "lab"
    ],
    "Entertainment": [
        "netflix", "spotify", "youtube", "amazon prime", "hotstar", "zee5",
        "bookmyshow", "pvr", "inox", "movies", "theatre", "concert", "disney",
        "music", "gaming", "steam", "playstation"
    ],
    "Utilities": [
        "electricity", "bsnl", "jio", "airtel", "vi ", "vodafone", "idea",
        "water", "gas", "cylinder", "lpg", "bescom", "mseb", "tata power",
        "postpaid", "broadband", "internet", "wifi", "recharge"
    ],
    "Rent & Housing": [
        "rent", "pg", "hostel", "maintenance", "society", "housing", "flat",
        "apartment", "lease"
    ],
    "Groceries": [
        "blinkit", "zepto", "instamart", "dunzo", "jiomart", "bigbasket",
        "grofers", "grocery", "vegetables", "fruits", "kirana", "reliance fresh",
        "more ", "spencers", "nature's basket"
    ],
    "Transfers & Payments": [
        "upi", "neft", "imps", "rtgs", "transfer", "payment", "wallet",
        "paytm", "phonepe", "gpay", "google pay", "mobikwik", "freecharge",
        "bank transfer", "self transfer"
    ],
    "Investments": [
        "zerodha", "groww", "upstox", "angel", "mutual fund", "mf", "sip",
        "stock", "share", "nse", "bse", "demat", "fd", "fixed deposit", "ppf",
        "nps", "elss"
    ],
    "Insurance": [
        "lic", "hdfc life", "icici prudential", "max life", "term plan",
        "insurance", "premium", "bajaj allianz", "new india", "policy"
    ],
    "Education": [
        "coursera", "udemy", "unacademy", "byju", "vedantu", "school", "college",
        "university", "fees", "tuition", "exam", "books", "stationery"
    ],
}

# Normalised merchant names — UPI handle suffix → clean name
UPI_MERCHANT_MAP = {
    "paytm": "Paytm",
    "oksbi": "SBI UPI",
    "okhdfcbank": "HDFC UPI",
    "okaxis": "Axis UPI",
    "okicici": "ICICI UPI",
    "ybl": "PhonePe",
    "ibl": "PhonePe",
    "axl": "Amazon Pay",
    "apl": "Amazon Pay",
}


def _normalise_merchant(description: str) -> str:
    """Strip UPI handles, extra spaces, and title-case the result."""
    if not description:
        return "Unknown"

    # Replace UPI handle with known merchant if possible
    upi_match = re.search(r"@(\w+)", description, re.IGNORECASE)
    if upi_match:
        handle = upi_match.group(1).lower()
        for key, name in UPI_MERCHANT_MAP.items():
            if key in handle:
                return name
        # Otherwise strip the @handle and clean up
        description = re.sub(r"@\w+", "", description).strip()

    # Remove reference numbers like "Ref 123456789012" or "UPI/12345"
    description = re.sub(r"\b(?:ref\.?\s*\w+|upi/\w+|txn\s*#?\s*\w+)\b", "", description, flags=re.IGNORECASE)

    # Clean repeated spaces
    description = re.sub(r"\s{2,}", " ", description).strip()

    return description.title() if description else "Unknown"


def _auto_categorize(description: str) -> str:
    """Return best-matching category based on keyword matching."""
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                return category
    return "Other"


def _parse_date_safe(raw: Any) -> str:
    """Safely parse a date string to YYYY-MM-DD."""
    if not raw:
        return datetime.today().strftime("%Y-%m-%d")
    raw_str = str(raw).strip()
    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d-%b-%Y"]:
        try:
            return datetime.strptime(raw_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return datetime.today().strftime("%Y-%m-%d")


class NormalizationService:
    """Converts a list of ParsedRows into canonical Transaction DB records."""

    def normalize(
        self,
        db: Session,
        user_id: int,
        parsed_rows: List[ParsedRow],
        source_type: str,  # "pdf" | "csv" | "sms"
        source_reference_id: int | None = None,
    ) -> List[Transaction]:
        """
        Normalize parsed rows and bulk-insert into the transactions table.
        Returns the list of created Transaction objects.
        """
        created = []

        for row in parsed_rows:
            merchant = _normalise_merchant(row.get("description", ""))
            category = _auto_categorize(merchant + " " + row.get("description", ""))
            amount = float(row.get("amount", 0))
            direction = row.get("direction", "debit")
            date_str = _parse_date_safe(row.get("date"))

            if amount <= 0:
                continue

            txn = Transaction(
                user_id=user_id,
                date=date_str,
                merchant=merchant,
                amount=amount,
                category=category,
                direction=direction,
                source_type=source_type,
                source_reference_id=str(source_reference_id) if source_reference_id else None,
                payment_mode="",
                notes=row.get("description", ""),
            )
            db.add(txn)
            created.append(txn)

        db.commit()
        return created


# Singleton instance
normalization_service = NormalizationService()
