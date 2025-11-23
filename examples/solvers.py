"""
Numerical solvers comparison using the new Symbolic API.

This example compares numerical solvers based on Euler
method and RK4.
"""
from mead import Stock, Flow, Model, Constant
import numpy as np # Keep for generating analytical solution for comparison

steps = 100
time_step = 0.25
growth_rate_val = 0.1 # 10% compounded growth

# Setup two models for comparison
euler_model = Model("Euler Model", dt=time_step)
rk4_model = Model("RK4 Model", dt=time_step)

# Define constants
exp_growth_rate = Constant("exp_growth_rate", growth_rate_val)

# Each method needs its own stock
euler_stock = Stock("euler", initial_value=1)
rk4_stock = Stock("rk4", initial_value=1)

# Same flow for both stocks, 10% compounded growth
# stock = stock + (stock * 0.1)
exp_growth_eq_euler = euler_stock * exp_growth_rate
euler_exp_growth_flow = Flow("exp_growth_flow", equation=exp_growth_eq_euler)

exp_growth_eq_rk4 = rk4_stock * exp_growth_rate
rk4_exp_growth_flow = Flow("exp_growth_flow", equation=exp_growth_eq_rk4)

# Wire stocks and flows, add them to the model
euler_stock.add_inflow(euler_exp_growth_flow)
euler_model.add(euler_stock, exp_growth_rate, euler_exp_growth_flow)

rk4_stock.add_inflow(rk4_exp_growth_flow)
rk4_model.add(rk4_stock, exp_growth_rate, rk4_exp_growth_flow)

# Euler method simulation
results_euler = euler_model.run(duration=steps, method="euler")
# RK4 method simulation
results_rk4 = rk4_model.run(duration=steps, method="rk4")

# Combine results for comparison
results = pd.DataFrame({'time': results_euler.index, 'euler': results_euler['euler'], 'rk4': results_rk4['rk4']})
results = results.set_index("time")

# Numpy direct exp calculation (for analytical comparison)
time_points = results.index
results["numpy_analytical"] = np.exp(time_points * growth_rate_val)

# Print last 10 results
print(results.tail(10))
