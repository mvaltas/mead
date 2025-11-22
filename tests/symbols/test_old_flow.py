from pytest import approx
from mead.symbols import Flow


def test_computes_a_formula():
    flow = Flow("test_flow", lambda: 0.1 + 0.2)
    assert flow.compute() == approx(0.3)
