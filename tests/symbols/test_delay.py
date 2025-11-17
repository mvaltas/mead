from mead.symbols import Delay, Constant

def test_delay_behavior():
    constant_rate = Constant("Constant rate", value=2)
    delayed = Delay("Simple delay", steps = 2, input=constant_rate)
    assert delayed.compute(step=0) == 0
    assert delayed.compute(step=1) == 0
    assert delayed.compute(step=2) == 2.0
    assert delayed.compute(step=3) == 2.0
