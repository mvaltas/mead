import mead as m
from mead.scenario import Scenario, ScenarioRunner
from copy import replace


def test_scenario_executes_a_model():
    with m.Model("m", dt=1) as model:
        s = m.Stock("s", initial_value=0)
        c = m.Constant("c", 1)
        f = m.Flow("f", c)
        s.add_inflow(f)

    sc1 = Scenario("high", variants=[m.Constant("c", 4)])
    sc2 = Scenario("max", variants=[m.Flow("f", 100)])

    runner = ScenarioRunner(model)

    results = runner.run([sc1, sc2], duration=10)

    assert results["high"]["s"].iloc[-1] == 40
