from mead.symbols import Stock, Flow, Constant, GoalFlow
from mead.old_model import Model
from mead.graph import Graph

"""Run predator-prey simulation."""
prey_birth_rate = 0.5
predation_rate = 0.01
predator_efficiency = 0.002
predator_death_rate = 0.3

preys = Stock("Preys", initial_value=100)
predators = Stock("Predators", initial_value=10)

prey_births = Flow(
    "prey_births", 
    lambda: preys.value * prey_birth_rate)

prey_deaths = Flow(
    "Prey deaths",
    formula=lambda: preys.value * predators.value * predation_rate,
)

preys.add_inflow(prey_births)
preys.add_outflow(prey_deaths)

predator_births = Flow(
    "Predator births",
    lambda: predators.value * preys.value * predator_efficiency,
)

predator_deaths = Flow(
    "Predator deaths", 
    formula=lambda: predators.value * predator_death_rate
)

predators.add_inflow(predator_births)
predators.add_outflow(predator_deaths)

m = Model(steps=10000, dt=0.01, stocks=[preys, predators])

history = m.run()

#history["predator_deaths"] = predator_deaths.history
#history["prey_deaths"] = prey_deaths.history
#history["prey_births"] = prey_births.history

Graph().plot(history)
