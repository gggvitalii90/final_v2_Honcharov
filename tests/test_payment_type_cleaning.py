from pathlib import Path

import pandas as pd


def test_equal_first_payment_and_offer_total_fills_one_payment():
    deals = pd.read_csv(Path("data_clean") / "deals_clean.csv", low_memory=False)

    equal_amounts = (
        deals["Initial Amount Paid"].notna()
        & deals["Offer Total Amount"].notna()
        & (deals["Initial Amount Paid"].round(2) == deals["Offer Total Amount"].round(2))
    )

    assert not deals.loc[equal_amounts, "Payment Type"].isna().any()
