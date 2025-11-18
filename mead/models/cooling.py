import mead.symbols as ms
from mead.model import Model
from mead.graph import Graph

# Example from: https://www.iseesystems.com/resources/help/v10/Content/Reference/Integration%20methods/Euler's_method.htm
# comparing with our solution
temperature = ms.Stock("Temperature", initial_value=100)
constant = ms.Constant("Constant", 0.5)
cooling = ms.Flow("Cooling", formula=lambda: temperature.value * constant)
temperature.add_outflow(cooling)

m = Model()
m.add_stock(temperature)

history = m.run(8, dt=0.5)

Graph().plot(history)
