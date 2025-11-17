from mead.symbols import Stock, Flow, Auxiliary
from mead.model import Model
from mead.graph import Graph

temp = Stock("Temperature", initial_value=70)

target_temp = Auxiliary("Target temp", formula = lambda: 70)
env_temp = Auxiliary("Environment temp", formula = lambda: 60)

temp_lost_to_env = Flow("Lost to env", formula = lambda: 1 / (temp.value - env_temp.compute()))

temp_heater = Auxiliary("Heater power", formula = lambda: 1)

heater_active = Flow("Heater on", formula = lambda: temp_heater.compute() if temp.value < target_temp.compute() else 0 )

#temp.add_inflow(heater_active)
temp.add_outflow(temp_lost_to_env)

m = Model()
m.add_stock(temp)

history = m.run(steps = 20, dt=1)

Graph().plot(history)
