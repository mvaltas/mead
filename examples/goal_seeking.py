"""
Goal Seeking Model (First-Order Negative Feedback)

Demonstrates a balancing feedback loop where a stock approaches
a target value over time.

Structure:
- Stock: Inventory
- Flow: Adjustment (proportional to gap between current and target)
- Target: Desired inventory level
"""

from mead import Stock, Flow, Model


"""Run goal-seeking simulation."""
target_inventory = 1000
adjustment_time = 5

model = Model("Goal Seeking", dt=0.25)

inventory = Stock("inventory", initial_value=100)

def adjustment_rate(ctx):
    current = ctx["state"]["inventory"]
    gap = target_inventory - current
    return gap / adjustment_time

adjustment = Flow("adjustment", adjustment_rate)

inventory.add_inflow(adjustment)
model.add_stock(inventory)

results = model.run(duration=30, method="euler")

print(results.head(10))
print(f"\nFinal inventory: {results['inventory'].iloc[-1]:.2f}")
print(f"Target inventory: {target_inventory}")
print(f"Gap: {target_inventory - results['inventory'].iloc[-1]:.2f}")

model.plot(results, "inventory")
