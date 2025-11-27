import matplotlib.pyplot as plt
from mead import Model, Stock, Constant, Flow, Table, Auxiliary, Time, IfThenElse

with Model("Kaibab Plateau", dt=0.25) as model:
    # Initial constants
    area = Constant("Area (acres)", 800_000)
    max_food = Constant("Max Food Capacity [(kcal/Day) * Year]", 400_000_000)
    daily_req = Constant("Daily Requirement [kcal(deer*Day)]", 2000)
    feeding = Constant("Feeding Period", 1)

    # The two main stocks in this model, predators
    # are not treated as stock.
    deer = Stock("Deers", initial_value=4000)
    food = Stock("Food", initial_value=400_000_000)

    # Deer growth
    food_per_deer = Auxiliary("Feed per deer", food / deer)
    growth_rate_lookup = [
            (0,     -0.5),
            (500,   -0.15),
            (1000,  0),
            (1500,  0.15),
            (2000,  0.2),
            (10000, 0.2)]
    deer_growth_rate = Table("Growth Rate", food_per_deer, growth_rate_lookup)
    net_increase = Flow("Deer growth",  deer * deer_growth_rate)

    deer.add_inflow(net_increase)

    # Predators
    predator_rate_lookup = [
            (0,     0),
            (0.005, 3),
            (0.01,  13),
            (0.015, 28),
            (0.02,  51),
            (0.025, 56),
            (0.05,  56)]
    # Predation depends on prey density
    deer_density = Auxiliary("Deer Density", deer / area)
    predation_rate = Table("Predation Rate", deer_density, predator_rate_lookup)

    # Table of predator count 
    predator_lookup = [
            (0,  265),
            (5,  245),
            (10, 200),
            (15, 65),
            (20, 8),
            (25, 0),
            (30, 0),
            (35, 0),
            (40, 0),
            (50, 0)]

    # Instead of a stock, the number of predators is calculated
    # through lookup 
    predator = Table("Predators", Time("year"), predator_lookup)
    predation_loss = Flow("Predation loss", predator * predation_rate)

    deer.add_outflow(predation_loss)

    # Controlling food
    vegetation_density = Auxiliary("Vegetation Density", food / max_food)
    regen_rate_lookup = [
            (0,    35),
            (0.25, 15),
            (0.5,  5),
            (0.75, 1.5),
            (1,    1)]
    regen_time = Table("Regeneration Time", vegetation_density,  regen_rate_lookup)
    # Food regeneration till max capacity
    food_increase = Flow("Food increase", (max_food - food) / regen_time)
    food.add_inflow(food_increase)

    # Food outflow
    food_demand = Auxiliary("Food Demand", deer * daily_req)
    # Food loss is capped to its demand or to the food available
    food_loss = IfThenElse("Final Food Demand", food_demand >= food, food, food_demand)
    # Food consumed
    food_consumption = Flow("Food Consumption", food_loss)
    food.add_outflow(food_consumption)


results = model.run(duration=50, method = "euler")

# Graphing the results in three different axes
time_points = results.index

fig, ax1 = plt.subplots(figsize=(12, 7))
fig.subplots_adjust(right=0.8)

ax1.set_xlabel('Year')
ax1.set_ylabel('Deers')
l1, =  ax1.plot(time_points, results['Deers'], label='Deers')
ax1.grid(True)
ax1.set_title(f"Kaibab Plateau - Deers, Food and Predators")

ax2 = ax1.twinx()
ax2.set_ylabel('Food')
l2, = ax2.plot(time_points, results['Food'], label='Food', color='tab:red')

ax3 = ax1.twinx()
ax3.set_ylabel('Predators')
l3, = ax3.plot(time_points, results['Predators'], label='Predators', color='tab:green')
ax3.spines.right.set_position(("axes", 1.2))

ax1.legend(handles=[l1, l2, l3])

plt.show()
