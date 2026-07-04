from pathlib import Path

import pandas as pd


DEALS_COLUMNS = [
    'Id', 'Created Time', 'Closing Date', 'Stage', 'Source', 'Campaign',
    'Product', 'Education Type', 'Payment Type', 'Initial Amount Paid',
    'Offer Total Amount', 'Quality', 'Deal Owner Name', 'City',
    'Level of Deutsch', 'Course duration', 'Months of study',
    'amount_error', 'closing_date_error'
]
SPEND_COLUMNS = ['Date', 'Source', 'Campaign', 'Spend', 'Clicks', 'Impressions', 'AdGroup', 'Ad']


def test_google_sheets_unit_exports_exist_with_expected_columns_and_rows():
    export_dir = Path('exports/google_sheets')
    deals_export = export_dir / 'deals_unit_clean.csv'
    spend_export = export_dir / 'spend_unit_clean.csv'

    assert deals_export.exists(), f'Missing Google Sheets export: {deals_export}'
    assert spend_export.exists(), f'Missing Google Sheets export: {spend_export}'

    deals = pd.read_csv(deals_export, low_memory=False)
    spend = pd.read_csv(spend_export, low_memory=False)

    assert list(deals.columns) == DEALS_COLUMNS
    assert list(spend.columns) == SPEND_COLUMNS
    assert len(deals) == len(pd.read_csv('data_clean/deals_clean.csv', low_memory=False))
    assert len(spend) == len(pd.read_csv('data_clean/spend_clean.csv', low_memory=False))
