"""
Goal Seeking Model

Demonstrates a negative feedback loop where a stock adjusts towards a target.
"""
from mead import Stock, Flow, Model, Constant, Equation


"""Run goal seeking simulation."""
model = Model("Goal Seeking", dt=0.25)

# 1. Define constants
target_val = Constant("target_val", 1000)
adjustment_time = Constant("adjustment_time", 5)

# 2. Define stock
inventory = Stock("inventory", initial_value=100)

# 3. Define symbolic equations
# The gap is the difference between the target and the current inventory
gap = target_val - inventory
# The adjustment rate is the gap divided by the adjustment time
adjustment_eq = gap / adjustment_time

# 4. Create the flow using the symbolic equation
adjustment = Flow("adjustment", equation=adjustment_eq)

# 5. Connect the flow to the stock
inventory.add_inflow(adjustment)

# 6. Add all elements to the model
model.add(inventory, target_val, adjustment_time, gap, adjustment)

# 7. Run the simulation
results = model.run(duration=30)

print(results.head(10))
print(f"\nFinal inventory: {results['inventory'].iloc[-1]:.2f}")
