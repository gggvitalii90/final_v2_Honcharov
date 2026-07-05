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


def test_google_sheets_upload_uses_new_sheet_id():
    from scripts.upload_google_sheets_clean_inputs import GOOGLE_SHEET_ID

    assert GOOGLE_SHEET_ID == '1ybv6r_ZyLiyFJv0SggjvJQaiYa568UYCv9r6ml6uIsg'


def test_old_google_sheet_id_is_not_referenced_in_project_workflow_files():
    old_sheet_id = '1ZVNBl54Qcimn4el49RGKoj8Trxj_rH2DmxJKvI6SAmI'
    workflow_files = [
        Path('PROJECT_DECISIONS.md'),
        Path('PROJECT_NAVIGATION.md'),
        Path('PROJECT_PLAN.md'),
        Path('notebooks/04_unit_economics.ipynb'),
        Path('scripts/upload_google_sheets_clean_inputs.py'),
    ]

    for path in workflow_files:
        assert old_sheet_id not in path.read_text(encoding='utf-8'), path

