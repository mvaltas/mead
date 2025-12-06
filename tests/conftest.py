import pytest


@pytest.fixture
def ctx():
    dummy_context = {
        "state": {"stock_val": 10, "other_stock": 20},
        "time": 0.0,
        "history_lookup": lambda name, time_ago: 5.0,  # Always returns 5.0 for simplicity
    }
    return dummy_context
