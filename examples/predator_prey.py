"""
Predator-Prey Model (Lotka-Volterra) with the new symbolic API.
"""
from mead import Stock, Flow, Model, Constant

# 1. Define constants for the rates
prey_birth_rate = Constant("prey_birth_rate", 0.5)
predation_rate = Constant("predation_rate", 0.01)
predator_efficiency = Constant("predator_efficiency", 0.002)
predator_death_rate = Constant("predator_death_rate", 0.3)

# 2. Create the model
model = Model("Predator-Prey", dt=0.01)

# 3. Define stocks
prey = Stock("prey", initial_value=100)
predators = Stock("predators", initial_value=10)

# 4. Define flows
prey_births = Flow("prey_births", equation = prey * prey_birth_rate)
prey_deaths = Flow("prey_deaths", equation = predation_rate * prey * predators)
predator_births = Flow("predator_births", equation = predator_efficiency * prey * predators)
predator_deaths = Flow("predator_deaths", equation = predator_death_rate * predators)

# 5. Connect flows to stocks
prey.add_inflow(prey_births)
prey.add_outflow(prey_deaths)
predators.add_inflow(predator_births)
predators.add_outflow(predator_deaths)

# 6. Add all elements to the model
model.add(
    prey,
    predators,
    prey_birth_rate,
    predation_rate,
    predator_efficiency,
    predator_death_rate,
    prey_births,
    prey_deaths,
    predator_births,
    predator_deaths
)

# 7. Run the simulation
results = model.run(duration=100, method="rk4")

print(results.tail(10))
print(f"\nFinal prey: {results['prey'].iloc[-1]:.2f}")
print(f"Final predators: {results['predators'].iloc[-1]:.2f}")

model.plot(results)
