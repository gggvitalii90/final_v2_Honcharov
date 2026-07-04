"""Create lightweight clean CSV inputs for Google Sheets unit economics.

The full clean CSV files stay in data_clean/. These exports contain only the
columns needed for the product analytics workbook, keeping Sheets easier to
inspect and recalculate.
"""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_clean"
EXPORT_DIR = BASE_DIR / "exports" / "google_sheets"

DEALS_COLUMNS = [
    "Id", "Created Time", "Closing Date", "Stage", "Source", "Campaign",
    "Product", "Education Type", "Payment Type", "Initial Amount Paid",
    "Offer Total Amount", "Quality", "Deal Owner Name", "City",
    "Level of Deutsch", "Course duration", "Months of study",
    "amount_error", "closing_date_error",
]
SPEND_COLUMNS = ["Date", "Source", "Campaign", "Spend", "Clicks", "Impressions", "AdGroup", "Ad"]


def _select_columns(df: pd.DataFrame, columns: list[str], source_name: str) -> pd.DataFrame:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise KeyError(f"{source_name} is missing required columns: {missing}")
    return df.loc[:, columns]


def export_google_sheets_inputs(
    data_dir: Path = DATA_DIR,
    export_dir: Path = EXPORT_DIR,
) -> list[Path]:
    export_dir.mkdir(parents=True, exist_ok=True)

    deals = pd.read_csv(data_dir / "deals_clean.csv", low_memory=False)
    spend = pd.read_csv(data_dir / "spend_clean.csv", low_memory=False)

    outputs = [
        (export_dir / "deals_unit_clean.csv", _select_columns(deals, DEALS_COLUMNS, "deals_clean.csv")),
        (export_dir / "spend_unit_clean.csv", _select_columns(spend, SPEND_COLUMNS, "spend_clean.csv")),
    ]

    written: list[Path] = []
    for path, df in outputs:
        df.to_csv(path, index=False, encoding="utf-8-sig")
        written.append(path)

    return written


if __name__ == "__main__":
    for path in export_google_sheets_inputs():
        print(path)
