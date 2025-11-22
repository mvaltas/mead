"""
Exponential Growth Model

Demonstrates a simple positive feedback loop where population grows
at a constant fractional rate.

Structure:
- Stock: Population
- Flow: Births (proportional to population)
"""

from mead import Stock, Flow, Model, fractional


"""Run exponential growth simulation."""
model = Model("Exponential Growth", dt=0.25)

population = Stock("population", initial_value=100)

birth_rate = 0.1
births = Flow("births", fractional("population", birth_rate))

population.add_inflow(births)
model.add_stock(population)

results = model.run(duration=50, method="euler")

print(results.head(10))
print(f"\nFinal population: {results['population'].iloc[-1]:.2f}")

model.plot(results, "population")
