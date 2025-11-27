from mead import Model, Stock, Flow, Constant, Hold

# A supply chain model with delayed replenishment
model = Model(name="Simple Supply Chain", dt=1)

inventory = Stock("inventory", initial_value=10)
port = Stock("port", initial_value=0)

order_fraction = Constant("order_fraction", 0.9)
logistics_eff_const = Constant(
    "logistics_eff_const", 1.0
)  # Assumed 100% of port stock

# Inflow to port: rate we order new shipments
order_rate_flow = Flow("order_rate", equation=inventory * order_fraction)
port.add_inflow(order_rate_flow)

# Outflow from port: port logistics efficiency
# Assuming logist_efficiency is a direct outflow from port based on its current value
logistics_eff_flow = Flow(
    "logistics_efficiency", equation=port * logistics_eff_const
)  # Assuming it clears port
port.add_outflow(logistics_eff_flow)


# Outflow from inventory: sales from inventory
sales_rate = Constant("sales_rage", 1.0)
sales_flow = Flow(
    "sales", equation=inventory * sales_rate
)  # Assuming it clears inventory if possible
inventory.add_outflow(sales_flow)

# Inflow to inventory: delayed shipments from port
# We delay the value of the 'port' stock by 4 time units.
shipments_delayed = Hold("shipments_delayed_val", port, hold_time=4)
shipments_flow = Flow("shipments", equation=shipments_delayed)
inventory.add_inflow(shipments_flow)

# Add all elements to the model
model.add(
    inventory,
    port,
    order_fraction,
    logistics_eff_const,
    order_rate_flow,
    logistics_eff_flow,
    sales_flow,
    shipments_delayed,
    shipments_flow,
    sales_rate,
)


# Run the simulation
results = model.run(duration=50)

# Print results
print(results)

model.plot(results, columns=["inventory"])
