from mead import Model, Stock, Flow, Delay, Auxiliary, Policy, Constant

with Model("Chickens and Road Crossings", dt=0.1) as model:
    chickens = Stock("Chickens", initial_value=10)

    # 60% of the chickens lay eggs
    egg_lays = Flow("Egg Lays", chickens * 0.6)
    # it takes 7 days for an egg to hatch
    brooding = Delay("Brooding", egg_lays, 7)
    # 80% of the eggs actually hatch
    egg_hatch = Flow("Egg Hatch", brooding * 0.8)
    # 80% chickens attempt to cross the road
    cross_attempts = Auxiliary("Attempt to cross", chickens * 0.8)
    # 60% of the cross attempts are fatal
    road_cross = Flow("Fatal Crossing", cross_attempts * 0.6)
    # new chickens...(instantaneous grown)
    chickens.add_inflow(egg_hatch)
    # lost chickens to fatal cross...
    chickens.add_outflow(road_cross)

# Run the simulation for 100 days
results = model.run(duration=100)
# Plot the number of chickens
model.plot(results, columns=["Chickens"])
