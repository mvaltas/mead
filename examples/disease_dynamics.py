"""
Example based on Insight Maker tutorial
https://insightmaker.com/docs/sddisease
"""

from mead import *

with Model("Disease Dynamics", dt=0.1) as model:
    healthy = Stock("Healthy", 100)
    infected = Stock("Infected", 1)

    infection_rate = Constant("Infection Rate", 0.008)
    infection = Flow("Infection", infection_rate * healthy * infected)
    healthy.add_outflow(infection)
    infected.add_inflow(infection)

    immune = Stock("Immune")

    recovery_rate = Constant("Recovery Rate", 0.1)
    recovery = Flow("Recovery", infected * recovery_rate)
    infected.add_outflow(recovery)
    immune.add_inflow(recovery)


results = model.run(duration=20)
model.plot(results)
