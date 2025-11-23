"""
Exponential Growth Model

Demonstrates a simple positive feedback loop where population grows
at a constant fractional rate.
"""
from mead import Stock, Flow, Model, Constant

# 1. Create the model
model = Model("Exponential Growth", dt=0.25)

# 2. Define model elements
population = Stock("population", initial_value=100)
birth_rate = Constant("birth_rate", 0.1)

# 3. Define the flow with a symbolic equation
births = Flow("births", equation=population * birth_rate)

# 4. Connect the flow to the stock
population.add_inflow(births)

# 5. Add all elements to the model
model.add(population, birth_rate, births)

# 6. Run the simulation
results = model.run(duration=50, method="euler")

print(results.head(10))
print(f"\nFinal population: {results['population'].iloc[-1]:.2f}")
