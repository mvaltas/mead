"""Shows that you can extend models from other models
which allows some degree of composition within
models"""

from mead import *

with Model("Base Aging Model", dt=1) as aging_model:
    youth = Stock("Youth", initial_value=100)
    adults = Stock("Adults", initial_value=250)
    elders = Stock("Elders", initial_value=30)

    youth_aging = Flow("youth_aging", equation=youth / 20)
    youth.add_outflow(youth_aging)
    adult_aging = Flow("adult_aging", equation=adults / 40)
    adults.add_outflow(adult_aging)
    elder_aging = Flow("elder_aging", equation=elders / 80)
    elders.add_outflow(elder_aging)


with Model("Births and Deaths", dt=1) as births_death_model:
    # extend first to avoid deepcopy to fail due
    # circular references
    births_death_model.extend(aging_model)

    newborns = Stock("Newborns")
    deads = Stock("Deaths")
    birth_rate = Constant("Birth Rate", 0.02)
    # you can access stocks and elements by their name on the previous model
    births = Flow("Births", aging_model.stocks["Adults"] * birth_rate)
    newborns.add_inflow(births)

    youth.add_inflow(Flow("Teenagers", newborns / 13))
    deads.add_inflow(elder_aging)


# Run and plot the extended model...
results = births_death_model.run(duration=100)
births_death_model.plot(results)
