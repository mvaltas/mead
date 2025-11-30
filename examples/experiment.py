import numpy as np
from mead import Model, Stock, Flow, Constant, Experiment, ScenarioRunner


with Model(name="Predator-Prey", dt=0.01) as model:
    prey_birth_rate = Constant("prey_birth_rate", 0.5)
    predation_rate = Constant("predation_rate", 0.01)
    predator_efficiency = Constant("predator_efficiency", 0.002)
    predator_death_rate = Constant("predator_death_rate", 0.3)

    prey = Stock("preys", initial_value=100)
    predators = Stock("predators", initial_value=10)

    prey_births = Flow("prey_births", equation=prey * prey_birth_rate)
    prey_deaths = Flow("prey_deaths", equation=predation_rate * prey * predators)
    predator_births = Flow(
        "predator_births", equation=predator_efficiency * prey * predators
    )
    predator_deaths = Flow("predator_deaths", equation=predator_death_rate * predators)

    prey.add_inflow(prey_births)
    prey.add_outflow(prey_deaths)
    predators.add_inflow(predator_births)
    predators.add_outflow(predator_deaths)


experiment = Experiment("Experiment")

# Let's change the predator_death_rate
# from 0.3 to 0.8 by 0.1 steps and look
experiment.add_variant(predator_death_rate, value=np.arange(0.3, 0.8, 0.1))

# Run all scenarios from the experiment for 60 steps
results = ScenarioRunner(model).run(experiment.scenarios(), duration=60, method="rk4")

# show experiment details
print(experiment)

# Plot only the stocks
model.plot(results, columns=list(model.stocks.keys()))
