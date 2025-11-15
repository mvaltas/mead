from mead.symbols import Stock, Flow, Auxiliary
from mead.model import Model

# Population
population = Stock("Population", initial_value=1000)

# Rates...
birth_rate = Auxiliary("birth_rate", lambda: 0.02)
death_rate = Auxiliary("death_rate", lambda: 0.03)

# Flow: Flows in to population at birth rate, the rate is per couple
births = Flow(
    "births",
    formula=lambda: population.value * birth_rate.compute(),
)
population.add_inflow(births)

# Flow: flows out of population at death rate, the rate a constant
deaths = Flow(
    "deaths",
    formula=lambda: population.value * death_rate.compute(),
)
population.add_outflow(deaths)

# Create model
m = Model()
m.add_auxiliary(birth_rate)
m.add_auxiliary(death_rate)
m.add_flow(births)
m.add_flow(deaths)
m.add_stock(population)
# Run simulation
history = m.run(steps=50, dt=1.0)

# Print population over time
for h in history["Population"]:
    print(h)
