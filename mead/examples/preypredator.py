from mead.symbols import Stock, Flow, Constant, GoalFlow
from mead.model import Model
from mead.graph import Graph

preys = Stock("Preys", initial_value=40)
predators = Stock("Predators", initial_value=10)

max_preys = Constant("Prey maximum", 40)

prey_births = GoalFlow("Prey births", stock=preys, goal=max_preys, max_rate = 4)  

prey_hunt_rate = Constant("Predation rate", 0.05)
prey_deaths = Flow(
    "Prey deaths",
    formula=lambda: preys.value * (predators.value * prey_hunt_rate),
)

preys.add_inflow(prey_births)
preys.add_outflow(prey_deaths)

predator_death_rate = Constant("Predator death rate", 0.5)
predator_deaths = Flow(
    "Predator deaths", formula=lambda: predators.value * predator_death_rate
)

predator_birth_rate = Constant("Predator growth by eating", 0.03)
predator_births = Flow(
    "Predator births",
    lambda: predators.value * (preys.value * predator_birth_rate),
)

predators.add_inflow(predator_births)
predators.add_outflow(predator_deaths)

m = Model(steps=7000, dt=0.005, stocks=[preys, predators])

history = m.run()

#history["predator_deaths"] = predator_deaths.history
#history["prey_deaths"] = prey_deaths.history
#history["prey_births"] = prey_births.history

Graph().plot(history)
