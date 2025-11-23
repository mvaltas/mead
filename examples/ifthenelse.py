from mead import Flow, Model, Stock
from mead.components import IfThenElse, Initial

model = Model("Functions Demo", dt=1)

# Given an inventory of 100 and daily sales of 40% of inventory
inventory = Stock("inventory", initial_value=50)
sales = Flow("sales", inventory * 0.4)

# If inventory falls to <30% of the original stock
# order 20% more of the current inventory
start_stock = Initial("starting_stock", inventory)
trigger_order = IfThenElse("trigger_backfill", ((start_stock * 0.3) - inventory), inventory * 1.2, 0)
# backfill rate is managed by trigger_order
backfill = Flow("backfill", trigger_order)

# set in/out flows from inventory
inventory.add_inflow(backfill)
inventory.add_outflow(sales)

model.add(inventory, trigger_order, sales)

results = model.run(duration=40)
print(results.tail(20))

model.plot(results)
