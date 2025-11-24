from mead import Stock, Model
from mead.flow import Flow
from mead.components import Initial

model = Model("Functions Demo", dt=1)

# Two stocks that grow based on stock_a initial value
# but at different rates
stock_a = Stock("stock_a", initial_value=10)
stock_a_initial = Initial("stock_a_initial", stock_a)
stock_a.add_inflow(Flow("growth_a", stock_a_initial * 0.1))
stock_b = Stock("stock_b", initial_value=0)
stock_b.add_inflow(Flow("growth_b", stock_a_initial * 0.2))

model.add(stock_a, stock_b, stock_a_initial)

results = model.run(duration=20)

print(f"Results {results.tail(10)}")

model.plot(results)
