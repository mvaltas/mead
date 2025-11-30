"""Implements the example of Wikipedia
article at https://en.wikipedia.org/wiki/Stock_and_flow
"""

import math
from mead import Model, Stock, Flow, Function

with Model("Wikipedia Article", dt=1) as model:
    stock_A = Stock("Stock A", initial_value=10)
    stock_B = Stock("Stock B", initial_value=0)

    function = Function("Flow", lambda ctx: math.sin(ctx["time"] * math.radians(5)))

    stock_A.add_outflow(Flow("out", function))
    stock_B.add_inflow(Flow("in", function))

results = model.run(duration=36, method="euler")

print(results[["Flow", "Stock A", "Stock B"]])

model.plot(results, columns=["Stock A", "Stock B", "Flow"])
