"""
Numerical solvers comparison

This example compares numerical solvers based on Euler
method, RK4, and direct from Numpy
"""
import numpy as np
from mead import Stock, Flow, Model, fractional

steps = 100
time_step = 0.25

# Setup two models for comparison
euler_model = Model("Numerical solvers", dt=time_step)
rk4_model = Model("Numerical solvers", dt=time_step)

# Each method needs its own stock
euler_stock = Stock("euler", initial_value=1)
rk4_stock = Stock("rk4", initial_value=1)

# Same flow for both stocks, 10% compounded growth
# stock = stock + (stock * 0.1)
euler_exp_growth = Flow("exp_growth", fractional("euler", 0.1))
rk4_exp_growth = Flow("exp_growth", fractional("rk4", 0.1))

# Wire stocks and flows, add them to the model
euler_stock.add_inflow(euler_exp_growth)
euler_model.add_stock(euler_stock)
rk4_stock.add_inflow(rk4_exp_growth)
rk4_model.add_stock(rk4_stock)

# Euler method simulation
results = euler_model.run(duration=steps, method="euler")
# RK4 method simulation
rk4_results = rk4_model.run(duration=steps, method="rk4")
# Numpy direct exp calculation
time = np.linspace(1, 10, int(steps/time_step) + 1)
results["numpy"] = list(np.exp(time))

# Copy rk4 results to euler results simulation so
# we can plot both
results["rk4"] = rk4_results["rk4"]

# Print last 10 results
print(results.tail(10))

# Plot all stocks
euler_model.plot(results,  "numpy", "euler", "rk4")
