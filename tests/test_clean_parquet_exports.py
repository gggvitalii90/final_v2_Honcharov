from pathlib import Path

import pandas as pd


CLEAN_FILES = ['deals_clean', 'spend_clean', 'calls_clean', 'contacts_clean']


def test_clean_parquet_exports_exist_and_match_csv_rows():
    data_dir = Path('data_clean')

    for stem in CLEAN_FILES:
        csv_path = data_dir / f'{stem}.csv'
        parquet_path = data_dir / f'{stem}.parquet'

        assert csv_path.exists(), f'Missing source CSV: {csv_path}'
        assert parquet_path.exists(), f'Missing Power BI Parquet export: {parquet_path}'

        csv_rows = len(pd.read_csv(csv_path, low_memory=False))
        parquet_rows = len(pd.read_parquet(parquet_path))

        assert parquet_rows == csv_rows, f'{stem}: parquet row count differs from CSV'
