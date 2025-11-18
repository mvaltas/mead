import mead.symbols as ms
import math
from mead.model import Model
from mead.graph import Graph

inventory = ms.Stock("Inventory", initial_value=50)
target_inventory = ms.Constant("Target Inventory", 60)

adjust_inventory = ms.GoalFlow(
    "Inventory Adjustment",
    stock=inventory,
    goal=target_inventory,
    max_rate=50
)

adjust_delayed = ms.Delay("Inventory order delay", steps=3, input=adjust_inventory)

# Parameters
min_val = 1
max_val = 80
cycle_steps = 30  # number of steps to complete one full cycle

osc_demand = ms.Auxiliary(
    "Oscillator",
    formula=lambda: min_val + (max_val - min_val)/2 * (1 + math.sin(2 * math.pi * m.step / cycle_steps))
)

demand = ms.Flow("Sales form",lambda: min(inventory.value, float(osc_demand)))


# Connect flows
inventory.add_inflow(adjust_delayed)   # use delayed adjustment
inventory.add_outflow(demand)  # use smoothed sales

# Model
m = Model(steps=100, stocks=[inventory], dt=0.1)
history = m.run()

# Add flows to history
history['inv_adjustment'] = adjust_delayed.history
history['demand'] = demand.history

Graph().plot(history)

