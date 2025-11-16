from mead.symbols import Stock, Flow, Auxiliary
from mead.model import Model
from mead.graph import Graph

preys = Stock("Preys", initial_value=40)
predators = Stock("Predators", initial_value=10)

prey_birth_rate = Auxiliary("Prey growth", formula=lambda: 1.2)
prey_births = Flow(
    "Prey births", 
    formula=lambda: prey_birth_rate.compute() * preys.value
)

prey_hunt_rate = Auxiliary("Predation rate", lambda: 0.05)
prey_deaths = Flow(
    "Prey deaths",
    formula=lambda: preys.value * (predators.value * prey_hunt_rate.compute()),
)

preys.add_inflow(prey_births)
preys.add_outflow(prey_deaths)

predator_death_rate = Auxiliary("Predator death rate", lambda: 1.2)
predator_deaths = Flow(
    "Predator deaths", formula=lambda: predators.value * predator_death_rate.compute()
)

predator_birth_rate = Auxiliary("Predator growth by eating", lambda: 0.03)
predator_births = Flow(
    "Predator births",
    lambda: predators.value * (preys.value * predator_birth_rate.compute()),
)

predators.add_inflow(predator_births)
predators.add_outflow(predator_deaths)

m = Model()
m.add_stock(preys)
m.add_stock(predators)

history = m.run(steps=7000, dt=0.005)

Graph().plot(history)
