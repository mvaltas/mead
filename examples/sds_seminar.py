"""Adapted from System Dynamics Society - Introduction to Modeling Process
Seminar Series: https://youtu.be/_HfFxyC08mI?si=KDvleScuYRQ4ujIu
"""

from copy import replace
from mead import Stock, Flow, Model, Constant, Scenario, ScenarioRunner

with Model("Romeo and Juliet", dt=0.1) as model:
    romeo_love = Stock("Romeo's Love for Juliet", initial_value=0.5)
    juliet_love = Stock("Juliet's Love for Romeo", initial_value=0.5)

    frac_of_romeos = Constant("Fractional adaptation of Romeo's Love", value=0.5)
    frac_of_juliet = Constant("Fractional adaptation of Juliet's Love", value=0.5)
    romeo_perception = Flow("Change in Romeo's Love", juliet_love * frac_of_romeos)
    juliet_perception = Flow("Change in Juliet's love", romeo_love * frac_of_juliet)

    romeo_love.add_outflow(romeo_perception)
    juliet_love.add_inflow(juliet_perception)

scenarios = [
    Scenario("base", variants=[]),
    Scenario(
        "slower_adapt",
        variants=[
            replace(frac_of_romeos, value=0.1),
            replace(frac_of_juliet, value=0.1),
        ],
    ),
    Scenario(
        "fast_adapt",
        variants=[
            replace(frac_of_romeos, value=0.9),
            replace(frac_of_juliet, value=0.9),
        ],
    ),
    Scenario(
        "more_initial",
        variants=[
            # changes in stocks require readd flows
            replace(romeo_love, initial_value=1).add_outflow(romeo_perception),
            replace(juliet_love, initial_value=1).add_inflow(juliet_perception),
        ],
    ),
    Scenario("romeo_frac_zero", variants=[replace(frac_of_romeos, value=0)]),
]

runner = ScenarioRunner(model)
results = runner.run(scenarios, duration=60, method="rk4")
model.plot(results, columns=["Romeo's Love for Juliet", "Juliet's Love for Romeo"])
