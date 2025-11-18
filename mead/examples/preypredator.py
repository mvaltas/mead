from mead.symbols import Stock, Flow, Constant
from mead.model import Model
from mead.graph import Graph

preys = Stock("Preys", initial_value=40)
predators = Stock("Predators", initial_value=10)

prey_birth_rate = Constant("Prey growth", 1.2)

prey_births = Flow("Prey births", formula=lambda: prey_birth_rate * preys.value)

prey_hunt_rate = Constant("Predation rate", 0.05)
prey_deaths = Flow(
    "Prey deaths",
    formula=lambda: preys.value * (predators.value * prey_hunt_rate),
)

preys.add_inflow(prey_births)
preys.add_outflow(prey_deaths)

predator_death_rate = Constant("Predator death rate", 1.2)
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

m = Model(steps=7000, dt=0.005, stocks = [preys, predators])

history = m.run()

Graph().plot(history)
