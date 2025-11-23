from mead import Model, Stock
from mead.flow import Flow
from mead.components import Delay 

model = Model("Functions Demo", dt=1.0)

# Moving from source to target with delay
source_stock = Stock("source_stock", initial_value=0)
target_stock = Stock("target_stock", initial_value=0)

# Source has a rate of 1
source_inflow_rate = Flow("source_inflow", 1.0)
source_stock.add_inflow(source_inflow_rate)

# Create a delay of 3 steps and apply as the source
# of the flow into target stock
delayed_output = Delay("delay_inflow_by_3", source_inflow_rate, 3.0)
target_stock.add_inflow(Flow("delayed_by_3", delayed_output))

# Source inflow rate must be calculated to apply the delay
# but not the delay itself due the connection to source_inflow_rate
model.add(source_stock, target_stock, source_inflow_rate)

# Run the simulation
results = model.run(duration=20)
print(results.tail(20))

# Plotting selected key results
model.plot(results, columns = ['source_stock', 'target_stock'])
