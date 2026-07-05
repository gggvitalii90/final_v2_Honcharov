"""Copy cleaned Deals and Spend CSV files for Google Sheets import.

Google Sheets receives the same cleaned datasets produced by the cleaning step,
not a separate reduced schema. We only limit the number of tables: Deals and
Spend are needed for unit economics; Contacts and Calls stay in Python analysis.
"""

from pathlib import Path
import shutil


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_clean"
EXPORT_DIR = BASE_DIR / "exports" / "google_sheets"
EXPORT_FILES = ["deals_clean.csv", "spend_clean.csv"]


def export_google_sheets_inputs(
    data_dir: Path = DATA_DIR,
    export_dir: Path = EXPORT_DIR,
) -> list[Path]:
    export_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for filename in EXPORT_FILES:
        source = data_dir / filename
        target = export_dir / filename
        if not source.exists():
            raise FileNotFoundError(f"Missing source CSV: {source}")
        shutil.copy2(source, target)
        written.append(target)

    return written


if __name__ == "__main__":
    for path in export_google_sheets_inputs():
        print(path)
