# MEAD: Modeling Environment for Analysis of Dynamics

`mead` is a simple Python framework for system dynamics modeling, allowing you
to build and simulate models using stocks, flows, and other components.

The name 'mead' is not only a type of beverage but also an homage to [Donella
Meadows](https://donellameadows.org/), a pioneering system dynamics thinker and
educator.

## Usage

Here is a simple example of an exponential growth model:

```python
from mead import Stock, Flow, Model, Constant

# Create a model
model = Model("Exponential Growth", dt=0.25)

# Create components
population = Stock("population", initial_value=100)
birth_rate = Constant("birth_rate", 0.1)
births = Flow("births", equation=population * birth_rate)

# Connect the components
population.add_inflow(births)

# Add components to the model
model.add(population, birth_rate, births)

# Run the simulation
results = model.run(duration=50)

# Print and plot the results
print(results.head())
model.plot(results)
```

This will produce a pandas DataFrame with the simulation results and a plot of
the 'population' stock over time. The directory `examples/` has other
examples of this framework usage.
