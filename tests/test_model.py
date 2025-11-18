from mead.model import Model
from mead.symbols import Stock, Constant


def test_model_returns_empty_history_with_no_stocks():
    m = Model(steps=1, dt=1)
    history = m.run()
    assert history == {}


def test_model_call_compute_to_stocks():
    m = Model(steps=2, dt=1)
    s = Stock("test", initial_value=0)
    c = Constant("simple", 1.0)
    s.add_inflow(c)
    m.add_stock(s)
    history = m.run()
    assert s.value == 2.0
    assert "test" in history
