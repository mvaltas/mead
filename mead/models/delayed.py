from mead.symbols import Stock, Delay, Constant, Flow
from mead.model import Model
from mead.graph import Graph

constant = Constant("Constant input", 1)

m = Model()

stock_A = Stock("StockA", initial_value=0)
delayed_inflow = Delay("delayed inflow", steps = 3, input = constant)
stock_A.add_inflow(delayed_inflow)

stock_B = Stock("StockB", initial_value=10)
delayed_outflow = Delay("delayed outflow", steps = 3, input = constant)
stock_B.add_outflow(delayed_outflow)

stock_C = Stock("StockC", initial_value=0)
maxed_input = Flow("maxed input", lambda: constant.compute() if stock_C.value < 9 else 0)
delay_sync = Delay("hold to sync", steps=1, input = maxed_input)
stock_C.add_inflow(delay_sync)

stock_D = Stock("StockD", initial_value=10)
delay_sync = Delay("hold to sync", steps=1, input = constant)
stock_D.add_outflow(delay_sync)

m.add_stock(stock_A)
m.add_stock(stock_B)
m.add_stock(stock_C)
m.add_stock(stock_D)

history = m.run(steps=13, dt=1)

Graph().plot(history)
