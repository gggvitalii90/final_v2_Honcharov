"""Upload full cleaned Deals and Spend CSV files to Google Sheets raw tabs.

This script does not calculate unit economics. It only refreshes the raw input
tabs in the separate Google Sheet used as the source of truth for formulas.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Iterable

import gspread
from google.oauth2.service_account import Credentials


BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "exports" / "google_sheets"
DEFAULT_CREDENTIALS_PATH = BASE_DIR / "google_credentials.json"
GOOGLE_SHEET_ID = "1ybv6r_ZyLiyFJv0SggjvJQaiYa568UYCv9r6ml6uIsg"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CSV_TO_WORKSHEET = {
    "deals_clean.csv": "01_deals_clean_raw",
    "spend_clean.csv": "02_spend_clean_raw",
}

METHODOLOGY_ROWS = [
    ["Rule", "Value"],
    ["Python role", "Clean data preparation and upload only"],
    ["Google Sheets role", "Source of truth for unit economics formulas"],
    ["Deals input", "Full exports/google_sheets/deals_clean.csv"],
    ["Spend input", "Full exports/google_sheets/spend_clean.csv"],
    ["Paid deal rule", "Stage = Payment Done AND Initial Amount Paid is not empty"],
    ["Base money metric", "First Payment Amount, not full recognized revenue"],
    ["Revenue recognition", "Separate scenario block; do not mix with base unit economics"],
]


def _credentials_path() -> Path:
    env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    return Path(env_path) if env_path else DEFAULT_CREDENTIALS_PATH


def _read_csv_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def _chunks(rows: list[list[str]], size: int = 1000) -> Iterable[list[list[str]]]:
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def _worksheet(sh: gspread.Spreadsheet, title: str, rows: int, cols: int) -> gspread.Worksheet:
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=max(rows, 1), cols=max(cols, 1))

    ws.resize(rows=max(rows, 1), cols=max(cols, 1))
    ws.clear()
    return ws


def _upload_rows(ws: gspread.Worksheet, rows: list[list[str]]) -> None:
    if not rows:
        return

    start_row = 1
    for chunk in _chunks(rows):
        ws.update(
            f"A{start_row}",
            chunk,
            value_input_option="USER_ENTERED",
        )
        start_row += len(chunk)


def upload_clean_inputs_to_google_sheets(
    sheet_id: str = GOOGLE_SHEET_ID,
    export_dir: Path = EXPORT_DIR,
    credentials_path: Path | None = None,
) -> str:
    credentials_path = credentials_path or _credentials_path()
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Google credentials not found: {credentials_path}. "
            "Add google_credentials.json or set GOOGLE_APPLICATION_CREDENTIALS."
        )

    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    sh = gspread.authorize(creds).open_by_key(sheet_id)

    for filename, worksheet_title in CSV_TO_WORKSHEET.items():
        rows = _read_csv_rows(export_dir / filename)
        max_cols = max((len(row) for row in rows), default=1)
        ws = _worksheet(sh, worksheet_title, rows=len(rows), cols=max_cols)
        _upload_rows(ws, rows)

    method_ws = _worksheet(sh, "03_methodology", rows=len(METHODOLOGY_ROWS), cols=2)
    _upload_rows(method_ws, METHODOLOGY_ROWS)

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}"


if __name__ == "__main__":
    print(upload_clean_inputs_to_google_sheets())
