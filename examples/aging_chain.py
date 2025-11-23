"""
Aging Chain Model (Birth-Death-Aging) with Symbolic API.
"""
from mead import Stock, Flow, Model, Constant

# 1. Define constants for rates and times
birth_rate_val = Constant("birth_rate_val", 0.02)
youth_aging_time = Constant("youth_aging_time", 20)
adult_aging_time = Constant("adult_aging_time", 45)
youth_death_rate = Constant("youth_death_rate", 0.001)
adult_death_rate = Constant("adult_death_rate", 0.005)
elderly_death_rate = Constant("elderly_death_rate", 0.05)

# 2. Create the model
model = Model("Aging Chain", dt=0.25)

# 3. Define stocks
youth = Stock("youth", initial_value=1000)
adults = Stock("adults", initial_value=3000)
elderly = Stock("elderly", initial_value=500)

# 4. Define flows using symbolic equations
births = Flow("births", equation=birth_rate_val * adults)

youth_aging = Flow("youth_aging", equation=youth / youth_aging_time)
adult_aging = Flow("adult_aging", equation=adults / adult_aging_time)

youth_deaths = Flow("youth_deaths", equation=youth_death_rate * youth)
adult_deaths = Flow("adults_deaths", equation=adult_death_rate * adults)
elderly_deaths = Flow("elderly_deaths", equation=elderly_death_rate * elderly)

# 5. Connect flows to stocks
youth.add_inflow(births)
youth.add_outflow(youth_aging)
youth.add_outflow(youth_deaths)

adults.add_inflow(youth_aging)
adults.add_outflow(adult_aging)
adults.add_outflow(adult_deaths)

elderly.add_inflow(adult_aging)
elderly.add_outflow(elderly_deaths)

# 6. Add all elements to the model
model.add(
    youth,
    adults,
    elderly,
    birth_rate_val,
    youth_aging_time,
    adult_aging_time,
    youth_death_rate,
    adult_death_rate,
    elderly_death_rate,
    births,
    youth_aging,
    adult_aging,
    youth_deaths,
    adult_deaths,
    elderly_deaths
)

# 7. Run the simulation
results = model.run(duration=200, method="euler")

print(results.head(10))
print(f"\nFinal populations:")
print(f"  Youth: {results['youth'].iloc[-1]:.2f}")
print(f"  Adults: {results['adults'].iloc[-1]:.2f}")
print(f"  Elderly: {results['elderly'].iloc[-1]:.2f}")
