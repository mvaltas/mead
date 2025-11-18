from mead.symbols import Stock, Flow
from mead.model import Model
from mead.graph import Graph

import numpy as np

# Euler method constraints
# > 1000 steps at dt=0.01 will
# approach a exp result
steps = 1000
dt = 10 / steps

quantity = Stock("quantity", initial_value=1)
growth = Flow("exponential", lambda: quantity.value)

quantity.add_inflow(growth)

m = Model(steps=steps, dt=dt)
m.add_stock(quantity)

history = m.run()

time = np.linspace(1, 10, steps + 1)
history["numpy"] = list(np.exp(time))

Graph().plot(history)
