"""
Goal Seeking Model

Demonstrates a negative feedback loop where a stock adjusts towards a target.
"""

from mead import Stock, Model, Constant
from mead.flow import goal_flow

"""Run goal seeking simulation."""
model = Model("Goal Seeking", dt=0.25)

target_val = Constant("target_val", 100)
adjustment_time = Constant("adjustment_time", 5)

inventory = Stock("inventory", initial_value=10)

adjustment = goal_flow("adjustment", inventory, target_val, adjustment_time)

# 5. Connect the flow to the stock
inventory.add_inflow(adjustment)

# 6. Add all elements to the model
model.add(inventory, target_val, adjustment_time, adjustment)

# 7. Run the simulation
results = model.run(duration=30)

print(results.head(10))
print(f"\nFinal inventory: {results['inventory'].iloc[-1]:.2f}")
model.plot(results)
