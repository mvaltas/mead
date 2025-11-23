from mead import Flow, Model, Stock
from mead.components import Min, Max

model = Model("Functions Demo", dt=1.0)

# stock a will decrease at 10% rate
stock_a = Stock("stock_a", initial_value=20)
stock_a.add_outflow(Flow("decrease", stock_a * 0.1))

# min will be at 7 and when stock a goes bellow, min will catch-up
min_output = Min("min", stock_a, 7) 
# max will match stock a until goes bellow 13, than it will stay at 13
max_output = Max("max", stock_a, 13) 

model.add(stock_a, min_output, max_output)

results = model.run(duration=20)
print(results.tail(10))

model.plot(results)
