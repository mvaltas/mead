from copy import replace
import mead as m
from mead.scenario import Scenario, ScenarioRunner


def test_scenario_executes_model():
    with m.Model("m", dt=1) as model:
        s = m.Stock("s", initial_value=0)
        c = m.Constant("c", 1)
        f = m.Flow("f", c)
        s.add_inflow(f)

    sc1 = Scenario("high", variants=[m.Constant("c", 4)])
    sc2 = Scenario("max", variants=[m.Constant("c", 10)])
    sc3 = Scenario("replaced", variants=[replace(c, value=40)])

    runner = ScenarioRunner(model)

    results = runner.run_many([sc1, sc2, sc3], duration=10)

    assert results["high"].loc[10, "s"] == 40
    assert results["max"].loc[10, "s"] == 100
    assert results["replaced"].loc[10, "s"] == 400


def test_plot_scenarios(tmp_path):
    with m.Model("m", dt=1) as model:
        s = m.Stock("s", initial_value=0)
        c = m.Constant("c", 1)
        f = m.Flow("f", c)
        s.add_inflow(f)

        scenarios = [
            Scenario("base", variants=[]),
            Scenario("high", variants=[m.Constant("c", 4)]),
            Scenario("max", variants=[m.Constant("f", 100)]),
        ]

        runner = ScenarioRunner(model)
        results = runner.run_many(scenarios, duration=10)

        plot_file = tmp_path / "test_plot.png"
        model.plot(results, save_path=plot_file)

        assert plot_file.exists()
