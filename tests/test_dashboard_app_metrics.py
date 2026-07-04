import importlib


def test_dashboard_paid_requires_payment_done_and_first_payment_amount():
    app = importlib.import_module('dashboard.app')

    expected_paid = int((
        (app.deals_real['Stage'] == 'Payment Done')
        & app.deals_real['Initial Amount Paid'].notna()
    ).sum())

    assert app.total_paid == expected_paid


def test_dashboard_uses_first_payment_amount_name_for_unit_metrics():
    app = importlib.import_module('dashboard.app')

    assert 'First Payment Amount' in app.ue_channels.columns
    assert 'Revenue' not in app.ue_channels.columns
