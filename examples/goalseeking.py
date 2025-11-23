"""
Goal Seeking Model with Delay and Oscillatory Demand (Simplified)
"""
from mead import Stock, Flow, Model, Constant, Auxiliary, Delay, goal_flow
import math

# Constants
MIN_DEMAND = Constant("min_demand", 1)
MAX_DEMAND = Constant("max_demand", 80)
CYCLE_STEPS = Constant("cycle_steps", 30) # For oscillator, using model.dt to calculate time

# Model setup
model = Model("Goal Seeking with Delay", dt=0.1)

# Stocks
inventory = Stock("inventory", initial_value=50)
target_inventory = Constant("target_inventory", 60) # Target for goal seeking

# === Demand (simplified from oscillatory) ===
# For now, let's make demand a constant to simplify the math.sin issue.
# A full oscillatory demand would require a function for math.sin over time.
# Placeholder:
demand_constant = Constant("demand_value", 10)
demand = Flow("demand", equation=demand_constant) # Simplified to a constant demand for now


# === Inventory Adjustment (Goal Seeking Flow) ===
# Note: Original had max_rate, which is not supported by our current goal_flow helper.
adjust_inventory = goal_flow(
    "Inventory Adjustment",
    stock=inventory,
    target=target_inventory,
    adjustment_time=Constant("adj_time", 5) # Assume an adjustment time
)

# === Delayed Adjustment ===
# The adjustment to inventory is delayed.
adjust_delayed = Delay("Inventory order delay", input_stock=adjust_inventory.equation, delay_time=3.0) # Delay the result of the goal_flow equation
adjust_delayed_flow = Flow("Adjust Delayed Flow", equation=adjust_delayed)


# Connect flows
inventory.add_inflow(adjust_delayed_flow)
inventory.add_outflow(demand)

# Add all elements to the model
model.add(
    inventory,
    target_inventory,
    demand_constant, # Add the constant demand
    demand,
    adjust_inventory,
    adjust_delayed,
    adjust_delayed_flow,
    MIN_DEMAND, MAX_DEMAND, CYCLE_STEPS, # Add original constants, even if not used directly now
    Constant("adj_time", 5) # Add the constant used in goal_flow
)

# Run the simulation
results = model.run(duration=100)

# Print results
print(results.head(10))
print(f"\nFinal inventory: {results['inventory'].iloc[-1]:.2f}")
