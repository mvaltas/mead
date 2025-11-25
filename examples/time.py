from mead import Model, Time, Stock, Flow


model = Model("Time Component", dt=1)

stock = Stock("stock", initial_value=0)
flow = Flow("inflow", Time("year"))
stock.add_inflow(flow)

model.add(stock, flow)

results = model.run(duration=10)

model.plot(results, columns = ['stock', 'year'])

