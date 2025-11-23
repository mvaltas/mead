from pytest import approx
from mead import Model, Stock, Flow

import logging

# Checks Euler's method for a cooling ODE
# ref: https://www.iseesystems.com/resources/help/v10/Content/Reference/Integration%20methods/Euler's_method.htm
def test_cooling_eulers_method(caplog):
    caplog.set_level(logging.DEBUG)

    m = Model("Cooling", dt=0.5)
    temperature = Stock("temperature", initial_value=100)
    cooling = Flow("Cooling", equation=lambda ctx: ctx["state"]["temperature"] * 0.5)
    temperature.add_outflow(cooling)

    m.add_stock(temperature)

    results = m.run(8)

    assert results["temperature"][0] == approx(100, 0.01)
    assert results["temperature"][1] == approx(75.00, 0.01)
    assert results["temperature"][2] == approx(56.25, 0.01)
    assert results["temperature"][3] == approx(42.19, 0.01)
    assert results["temperature"][4] == approx(31.64, 0.01)
    assert results["temperature"][5] == approx(23.73, 0.01)
    assert results["temperature"][6] == approx(17.80, 0.01)
    assert results["temperature"][7] == approx(13.35, 0.01)
    assert results["temperature"][8] == approx(10.01, 0.01)
