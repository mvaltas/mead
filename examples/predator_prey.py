"""
Predator-Prey Model (Lotka-Volterra)

Demonstrates coupled feedback loops creating oscillatory behavior.

Structure:
- Stocks: Prey population, Predator population
- Flows: Prey births, Prey deaths (from predation), Predator births, Predator deaths
"""

from mead import Stock, Flow, Model


"""Run predator-prey simulation."""
prey_birth_rate = 0.5
predation_rate = 0.01
predator_efficiency = 0.002
predator_death_rate = 0.3

model = Model("Predator-Prey", dt=0.01)

prey = Stock("prey", initial_value=100)
predators = Stock("predators", initial_value=10)

def prey_births_rate(t, s):
    return prey_birth_rate * s.get("prey", 0)

prey_births = Flow("prey_births", prey_births_rate)

def predation(t, s):
    return predation_rate * s.get("prey", 0) * s.get("predators", 0)

prey_deaths = Flow("prey_deaths", predation)

def predator_births_rate(t, s):
    return predator_efficiency * s.get("prey", 0) * s.get("predators", 0)

predator_births = Flow("predator_births", predator_births_rate)

def predator_deaths_rate(t, s):
    return predator_death_rate * s.get("predators", 0)

predator_deaths = Flow("predator_deaths", predator_deaths_rate)

prey.add_inflow(prey_births)
prey.add_outflow(prey_deaths)

predators.add_inflow(predator_births)
predators.add_outflow(predator_deaths)

model.add_stock(prey)
model.add_stock(predators)

results = model.run(duration=100, method="rk4")

print(results.head(10))
print(f"\nFinal prey: {results['prey'].iloc[-1]:.2f}")
print(f"Final predators: {results['predators'].iloc[-1]:.2f}")

model.plot(results, "prey", "predators")

