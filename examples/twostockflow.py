from mead.symbols import Stock, Flow
from mead.old_model import Model
from mead.graph import Graph

stock_one = Stock("stock one", initial_value=0)
stock_two = Stock("stock two", initial_value=0)

source = Flow("Source", formula=lambda: 1)

flow_one_two = Flow("From one to two", formula=lambda: stock_one.value)

sink = Flow("Sink", formula=lambda: stock_two.value)

stock_one.add_inflow(source)

stock_one.add_outflow(flow_one_two)
stock_two.add_inflow(flow_one_two)

stock_two.add_outflow(sink)


m = Model(steps=1000, dt=0.01)
m.add_stock(stock_one)
m.add_stock(stock_two)

history = m.run()

Graph().plot(history)
