"""Export cleaned CSV datasets to Parquet for Power BI.

CSV remains the universal/checkable format. Parquet is an additional typed,
compact export for Power BI and other BI tools.
"""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_clean"
CLEAN_FILES = ["deals_clean", "spend_clean", "calls_clean", "contacts_clean"]


def export_clean_parquet(data_dir: Path = DATA_DIR) -> list[Path]:
    exported: list[Path] = []
    for stem in CLEAN_FILES:
        csv_path = data_dir / f"{stem}.csv"
        parquet_path = data_dir / f"{stem}.parquet"

        if not csv_path.exists():
            raise FileNotFoundError(f"Missing source CSV: {csv_path}")

        df = pd.read_csv(csv_path, low_memory=False)
        df.to_parquet(parquet_path, index=False, engine="pyarrow")
        exported.append(parquet_path)

    return exported


if __name__ == "__main__":
    for path in export_clean_parquet():
        print(path)
