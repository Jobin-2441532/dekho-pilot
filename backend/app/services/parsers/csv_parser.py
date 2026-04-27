"""
CSV Parser — extracts transaction rows from bank statement CSVs.
Handles UPI exports, HDFC/ICICI/Axis CSV formats via flexible column aliasing.
"""
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import re

import pandas as pd


ParsedRow = Dict[str, Any]

# Canonical key → possible column name aliases (all lowercase)
COLUMN_ALIASES = {
    "date": [
        "date", "txn date", "transaction date", "value date",
        "posting date", "settlement date"
    ],
    "description": [
        "description", "narration", "particulars", "remarks",
        "transaction remarks", "details", "upi ref"
    ],
    "debit": [
        "debit", "dr", "withdrawal amt", "withdrawal amount",
        "amount (dr)", "debit amount"
    ],
    "credit": [
        "credit", "cr", "deposit amt", "deposit amount",
        "amount (cr)", "credit amount"
    ],
    # Some CSVs have a single amount column + a type column
    "amount": ["amount", "transaction amount", "inr amount"],
    "type": ["type", "transaction type", "dr/cr", "debit/credit"],
}


def _match_column(df_columns: List[str], aliases: List[str]) -> str | None:
    norm = {c.lower().strip(): c for c in df_columns}
    for alias in aliases:
        if alias in norm:
            return norm[alias]
    return None


def _parse_amount(val) -> float:
    if pd.isna(val) or val == "":
        return 0.0
    cleaned = re.sub(r"[₹,\s]", "", str(val))
    try:
        return abs(float(cleaned))
    except ValueError:
        return 0.0


def _parse_date(raw: str) -> str:
    formats = [
        "%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d-%b-%Y",
        "%Y-%m-%d", "%d/%m/%y", "%m/%d/%Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(str(raw).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return str(raw).strip()


def parse_csv(file_path: str | Path) -> List[ParsedRow]:
    """
    Read a bank CSV and return a list of ParsedRow dicts.
    """
    rows: List[ParsedRow] = []

    try:
        df = pd.read_csv(str(file_path), encoding="utf-8", on_bad_lines="skip")
    except UnicodeDecodeError:
        df = pd.read_csv(str(file_path), encoding="latin-1", on_bad_lines="skip")

    df.columns = df.columns.str.strip()

    # Map canonical fields to actual column names
    date_col = _match_column(df.columns.tolist(), COLUMN_ALIASES["date"])
    desc_col = _match_column(df.columns.tolist(), COLUMN_ALIASES["description"])
    debit_col = _match_column(df.columns.tolist(), COLUMN_ALIASES["debit"])
    credit_col = _match_column(df.columns.tolist(), COLUMN_ALIASES["credit"])
    amount_col = _match_column(df.columns.tolist(), COLUMN_ALIASES["amount"])
    type_col = _match_column(df.columns.tolist(), COLUMN_ALIASES["type"])

    if not date_col or not desc_col:
        raise ValueError("CSV does not have recognisable date/description columns.")

    for _, row in df.iterrows():
        raw_date = str(row.get(date_col, "")).strip()
        raw_desc = str(row.get(desc_col, "")).strip()

        if not raw_date or raw_date.lower() in ("nan", ""):
            continue

        # Determine amount and direction
        if debit_col and credit_col:
            debit_amt = _parse_amount(row.get(debit_col))
            credit_amt = _parse_amount(row.get(credit_col))
            if debit_amt == 0 and credit_amt == 0:
                continue
            direction = "debit" if debit_amt > 0 else "credit"
            amount = debit_amt if debit_amt > 0 else credit_amt
        elif amount_col:
            amount = _parse_amount(row.get(amount_col))
            if amount == 0:
                continue
            raw_type = str(row.get(type_col, "")).lower() if type_col else ""
            direction = "credit" if any(k in raw_type for k in ["cr", "credit"]) else "debit"
        else:
            continue

        rows.append({
            "date": _parse_date(raw_date),
            "description": raw_desc,
            "amount": amount,
            "direction": direction,
        })

    return rows
