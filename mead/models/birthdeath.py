from mead.symbols import Stock, Flow, Auxiliary
from mead.model import Model
import mead.graph
from random import random

# Population...
population = Stock("Population", initial_value=10_000)

# Rates...
birth_rate = Auxiliary("birth_rate", lambda: random())
death_rate = Auxiliary("death_rate", lambda: random())

# Births as rate in population
births = Flow("births", formula=lambda: population.value * birth_rate)
population.add_inflow(births)

# Deaths as rate in population
deaths = Flow("deaths", formula=lambda: population.value * death_rate)
population.add_outflow(deaths)

m = Model()
m.add_stock(population)

# Run simulation
history = m.run(steps=10_000, dt=0.01)

g = mead.graph.Graph()
g.plot(history)
