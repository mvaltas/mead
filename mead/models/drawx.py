import mead.symbols as ms
from mead.model import Model
from mead.graph import Graph

constant = ms.Constant("Constant input", 1)

m = Model()

stock_A = ms.Stock("StockA", initial_value=0)
delayed_inflow = ms.Delay("delayed inflow", steps = 3, input = constant)
stock_A.add_inflow(delayed_inflow)

stock_B = ms.Stock("StockB", initial_value=10)
delayed_outflow = ms.Delay("delayed outflow", steps = 3, input = constant)
stock_B.add_outflow(delayed_outflow)

stock_C = ms.Stock("StockC", initial_value=0)
maxed_input = ms.Flow("maxed input", lambda: constant.compute() if stock_C.value < 9 else 0)
delay_sync = ms.Delay("hold to sync", steps=1, input = maxed_input)
stock_C.add_inflow(delay_sync)

stock_D = ms.Stock("StockD", initial_value=10)
delay_sync = ms.Delay("hold to sync", steps=1, input = constant)
stock_D.add_outflow(delay_sync)

m.add_stock(stock_A)
m.add_stock(stock_B)
m.add_stock(stock_C)
m.add_stock(stock_D)

history = m.run(steps=13, dt=1)

Graph().plot(history)
