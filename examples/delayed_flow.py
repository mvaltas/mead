from mead import Model, Stock, Flow
from mead.flow import fractional, delayed, stock_total

# A suply chain that every three days can
# replishish only 80% of the inventory
model = Model(name="Simple Supply Chain", dt=1)

inventory = Stock("inventory", initial_value=10)
port = Stock("port", initial_value=0)

# rate we order new shipments, 90%
port.add_inflow(Flow("order_rate", fractional("inventory", 0.9)))
# port logistics, 100%
port.add_outflow(Flow("logist_efficiency", stock_total("port")))
# sales from inventory...
inventory.add_outflow(Flow("sales", stock_total("inventory")))

# delayed shippments
inventory.add_inflow(Flow("shipments", delayed("port", delay_time=4)))

# Add stocks to the model
model.add_stock(inventory)
model.add_stock(port)

# Run the simulation
results = model.run(duration=50)

# Print and plot
print(results)
model.plot(results, "inventory")
