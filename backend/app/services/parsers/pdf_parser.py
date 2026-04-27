"""
PDF Parser — extracts transaction rows from Indian bank statement PDFs.
Supports HDFC, ICICI, SBI, and Axis formats via heuristic column detection.
"""
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import pdfplumber


# ---------------------------------------------------------------------------
# ParsedRow type alias
# ---------------------------------------------------------------------------
ParsedRow = Dict[str, Any]  # keys: date, description, amount, direction

# ---------------------------------------------------------------------------
# Bank format column maps (header keyword → canonical key)
# ---------------------------------------------------------------------------
HDFC_HEADERS = {
    "date": ["date", "value dt"],
    "description": ["narration", "description", "particulars"],
    "debit": ["withdrawal amt", "debit", "debit amount", "dr"],
    "credit": ["deposit amt", "credit", "credit amount", "cr"],
}

ICICI_HEADERS = {
    "date": ["s no.", "date", "transaction date"],
    "description": ["transaction remarks", "description", "particulars"],
    "debit": ["amount (inr)", "debit", "withdrawal"],
    "credit": ["amount (inr)", "credit", "deposit"],
}

GENERIC_HEADERS = {
    "date": ["date", "txn date", "transaction date", "value date"],
    "description": ["description", "narration", "particulars", "remarks", "details"],
    "debit": ["debit", "dr", "withdrawal", "amount dr"],
    "credit": ["credit", "cr", "deposit", "amount cr"],
}


def _normalise_header(h: str) -> str:
    return h.lower().strip()


def _detect_column_map(headers: List[str]) -> Dict[str, int] | None:
    """Given a list of header strings, return index map for date/description/debit/credit."""
    norm = [_normalise_header(h) for h in headers]

    for fmt in [HDFC_HEADERS, ICICI_HEADERS, GENERIC_HEADERS]:
        col_map = {}

        for role, candidates in fmt.items():
            for c in candidates:
                if c in norm:
                    col_map[role] = norm.index(c)
                    break

        # Need at minimum: date + description + (debit or credit)
        if "date" in col_map and "description" in col_map and ("debit" in col_map or "credit" in col_map):
            return col_map

    return None


def _parse_amount(raw: str) -> float:
    """Strip currency symbols and commas, convert to float."""
    if not raw:
        return 0.0
    cleaned = re.sub(r"[₹,\s]", "", str(raw))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _parse_date(raw: str) -> str:
    """Try common Indian date formats and return YYYY-MM-DD."""
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d-%b-%Y", "%Y-%m-%d", "%d/%m/%y"]
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw.strip()  # fallback: return as-is


def parse_pdf(file_path: str | Path) -> List[ParsedRow]:
    """
    Open a bank statement PDF and extract transaction rows.
    Returns a list of ParsedRow dicts.
    """
    rows: List[ParsedRow] = []

    with pdfplumber.open(str(file_path)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue

                # First non-empty row is assumed to be headers
                header_row = table[0]
                if not any(header_row):
                    header_row = table[1]

                col_map = _detect_column_map(header_row)
                if not col_map:
                    continue  # Skip unrecognised table

                for row in table[1:]:
                    try:
                        raw_date = row[col_map["date"]] or ""
                        raw_desc = row[col_map.get("description", 1)] or ""

                        raw_debit = row[col_map["debit"]] if "debit" in col_map else ""
                        raw_credit = row[col_map["credit"]] if "credit" in col_map else ""

                        debit_amt = _parse_amount(raw_debit)
                        credit_amt = _parse_amount(raw_credit)

                        # Skip rows without meaningful amount
                        if debit_amt == 0 and credit_amt == 0:
                            continue

                        # Skip header-like rows that crept in
                        if not raw_date or re.match(r"[a-zA-Z]", raw_date.strip()):
                            continue

                        direction = "debit" if debit_amt > 0 else "credit"
                        amount = debit_amt if debit_amt > 0 else credit_amt

                        rows.append({
                            "date": _parse_date(raw_date),
                            "description": raw_desc.strip(),
                            "amount": amount,
                            "direction": direction,
                        })
                    except (IndexError, TypeError):
                        continue

    return rows
