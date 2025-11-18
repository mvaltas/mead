from pytest import approx
import mead.symbols as ms
from mead.model import Model

# Checks Euler's method for a cooling ODE
# ref: https://www.iseesystems.com/resources/help/v10/Content/Reference/Integration%20methods/Euler's_method.htm
def test_cooling_eulers_method():
    temperature = ms.Stock("Temperature", initial_value = 100)
    cooling = ms.Flow("Cooling", formula = lambda: temperature.value * 0.5)
    temperature.add_outflow(cooling)
    m = Model()
    m.add_stock(temperature)
    dt = 0.5
    m.run(steps=9, dt=dt)
    # temperature decay...
    assert temperature.history[0] == approx(100)
    assert temperature.history[1] == approx(75.00)
    assert temperature.history[2] == approx(56.25)
    assert temperature.history[3] == approx(42.19, 0.01)
    assert temperature.history[4] == approx(31.64, 0.01)
    assert temperature.history[5] == approx(23.73, 0.01)
    assert temperature.history[6] == approx(17.80, 0.01)
    assert temperature.history[7] == approx(13.35, 0.01)
    assert temperature.history[8] == approx(10.01, 0.01)

    # cooling decay...
    assert cooling.history[0] * dt == approx(25.00)
    assert cooling.history[1] * dt == approx(18.75, 0.01)
    assert cooling.history[2] * dt == approx(14.06, 0.01)
    assert cooling.history[3] * dt == approx(10.55, 0.01)
    assert cooling.history[4] * dt == approx(7.91, 0.01)
    assert cooling.history[5] * dt == approx(5.93, 0.01)
    assert cooling.history[6] * dt == approx(4.45, 0.01)
    assert cooling.history[7] * dt == approx(3.34, 0.01)
    assert cooling.history[8] * dt == approx(2.50, 0.01)

