"""
This example demonstrates how scenarios can be used to compare the system's
behavior.

We setup the same example of the chickens road crossings and compare
against different changes, in policy or rates in the system.
"""

from copy import replace
from mead import (
    Model,
    Stock,
    Flow,
    Delay,
    Auxiliary,
    Policy,
    Constant,
    Scenario,
    ScenarioRunner,
)

with Model("Chickens and Road Crossings", dt=0.1) as model:
    # our main stock, our chickens
    chickens = Stock("Chickens", initial_value=10)

    # 60% of the chickens lay eggs
    egg_lays = Flow("Egg Lays", chickens * 0.6)
    # it takes 7 days for an egg to hatch
    brooding = Delay("Brooding", egg_lays, 7)
    # 80% of the eggs actually hatch
    egg_hatch = Flow("Egg Hatch", brooding * 0.8)
    # new chickens...(instantaneous grown)
    chickens.add_inflow(egg_hatch)
    # 80% chickens attempt to cross the road
    fence_quality = Constant("Fence Quality", 0.8)
    cross_attempts = Auxiliary("Attempt to cross", chickens * fence_quality)
    # 60% of the cross attempts are fatal
    fatality = Constant("Fatality Rate", 0.6)
    road_cross = Flow("Fatal Crossing", cross_attempts * fatality)
    # set the fatalities as an outflow of chickens
    chickens.add_outflow(road_cross)
    # establish a policy of buying more chickens if our stock falls
    # under our initial stock by 50% or less
    replace_qty = Constant("Chicken Replacement", 5)
    policy = Policy(
        "buy_more", chickens < (chickens.initial_value * 0.5), replace_qty, apply=1
    )
    # Create an inflow from this policy
    policy_flow = Flow("Aplying Policy", policy)
    chickens.add_inflow(policy_flow)


# Create different scenarios for exploration
scenarios = [
    # base, no changes
    Scenario("base", variants=[]),
    # Better street signs less fatalities?
    Scenario("street_signals", variants=[Constant("Fatality Rate", 0.5)]),
    # Better containment, only 70% escape
    Scenario("better_fences", variants=[replace(fence_quality, value=0.7)]),
    # Apply our policy when less than 70% of the initial instead of 50%
    Scenario(
        "early_policy",
        variants=[replace(policy, condition=chickens < (chickens.initial_value * 0.7))],
    ),
    # Don't apply policy at all
    Scenario("no_policy", variants=[replace(policy, apply=0)]),
    # Apply twice in a row
    Scenario("policy_twice", variants=[replace(policy, apply=2)]),
    # Always apply policy '-1' means always apply
    Scenario("policy_always", variants=[replace(policy, apply=-1)]),
]

# Run the simulation for 100 days
# results = model.run(duration=100)
runner = ScenarioRunner(model)
results = runner.run(scenarios, duration=100)
# Plot the number of chickens
model.plot(results, columns=["Chickens"])
