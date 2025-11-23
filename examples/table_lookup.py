from mead import Flow, Model, Stock
from mead.components import Table

model = Model("Functions Demo", dt=1)

table_stock = Stock("table_stock", initial_value=1)
table_stock.add_inflow(Flow("inflow", table_stock * 0.2))

table_points = [(0,0), (5,50), (10,100), (15,50), (20,0)]
table_output = Table("table_output", table_stock, table_points)
model.add(table_stock, table_output)

results = model.run(duration=20)
print(results.tail(20))

model.plot(results)
