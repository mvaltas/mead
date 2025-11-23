"""
Aging Chain Model (Birth-Death-Aging)

Demonstrates a chain of stocks representing age cohorts with flows
between them representing aging, plus births and deaths.

Structure:
- Stocks: Youth (0-20), Adults (20-65), Elderly (65+)
- Flows: Births, Youth aging, Adult aging, Deaths
"""

from mead import Stock, Flow, Model


"""Run aging chain simulation."""
birth_rate = 0.02
youth_aging_time = 20
adult_aging_time = 45
youth_death_rate = 0.001
adult_death_rate = 0.005
elderly_death_rate = 0.05

model = Model("Aging Chain", dt=0.25)

youth = Stock("youth", initial_value=1000)
adults = Stock("adults", initial_value=3000)
elderly = Stock("elderly", initial_value=500)

def births_rate(ctx):
    return birth_rate * ctx["state"]["adults"]

births = Flow("births", births_rate)

def youth_aging_rate(ctx):
    return ctx["state"]["youth"] / youth_aging_time

youth_aging = Flow("youth_aging", youth_aging_rate)

def adult_aging_rate(ctx):
    return ctx["state"]["adults"] / adult_aging_time

adult_aging = Flow("adult_aging", adult_aging_rate)

def youth_deaths_rate(ctx):
    return youth_death_rate * ctx["state"]["youth"]

def adult_deaths_rate(ctx):
    return adult_death_rate * ctx["state"]["adults"]

def elderly_deaths_rate(ctx):
    return elderly_death_rate * ctx["state"]["elderly"]

youth_deaths = Flow("youth_deaths", youth_deaths_rate)
adult_deaths = Flow("adult_deaths", adult_deaths_rate)
elderly_deaths = Flow("elderly_deaths", elderly_deaths_rate)

youth.add_inflow(births)
youth.add_outflow(youth_aging)
youth.add_outflow(youth_deaths)

adults.add_inflow(youth_aging)
adults.add_outflow(adult_aging)
adults.add_outflow(adult_deaths)

elderly.add_inflow(adult_aging)
elderly.add_outflow(elderly_deaths)

model.add_stock(youth)
model.add_stock(adults)
model.add_stock(elderly)

results = model.run(duration=200, method="euler")

results["total"] = results["youth"] + results["adults"] + results["elderly"]

print(results.head(10))
print(f"\nFinal populations:")
print(f"  Youth: {results['youth'].iloc[-1]:.2f}")
print(f"  Adults: {results['adults'].iloc[-1]:.2f}")
print(f"  Elderly: {results['elderly'].iloc[-1]:.2f}")
print(f"  Total: {results['total'].iloc[-1]:.2f}")

model.plot(results, "youth", "adults", "elderly")
