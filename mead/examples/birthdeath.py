import mead.symbols as ms
from mead.model import Model
import mead.graph
from random import random

# Population...
population = ms.Stock("Population", initial_value=10_000)

# Rates...
birth_rate = ms.Auxiliary("birth_rate", lambda: random())
death_rate = ms.Auxiliary("death_rate", lambda: random())

# Births as rate in population
births = ms.Flow("births", formula=lambda: population.value * birth_rate)
population.add_inflow(births)

# Deaths as rate in population
deaths = ms.Flow("deaths", formula=lambda: population.value * death_rate)
population.add_outflow(deaths)

m = Model(steps=10_000, dt=0.01)
m.add_stock(population)

# Run simulation
history = m.run()

g = mead.graph.Graph()
g.plot(history)
