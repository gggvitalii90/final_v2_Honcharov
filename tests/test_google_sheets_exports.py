from pathlib import Path

import pandas as pd


EXPORT_FILES = ['deals_clean.csv', 'spend_clean.csv']


def test_google_sheets_exports_are_full_clean_deals_and_spend_csvs():
    export_dir = Path('exports/google_sheets')
    data_dir = Path('data_clean')

    for filename in EXPORT_FILES:
        clean_path = data_dir / filename
        export_path = export_dir / filename

        assert export_path.exists(), f'Missing Google Sheets export: {export_path}'

        clean = pd.read_csv(clean_path, low_memory=False)
        exported = pd.read_csv(export_path, low_memory=False)

        assert list(exported.columns) == list(clean.columns)
        assert len(exported) == len(clean)
