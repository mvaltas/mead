"""
Harmonic Oscillator Model using the new symbolic API.
"""

from mead import Stock, Flow, Model, Constant

# 1. Constants
m = Constant("mass", 1.0)  # mass
k = Constant("spring_constant", 1.0)  # spring constant
c = Constant("damping", 0.0)  # damping

# 2. Model
model = Model("Harmonic Oscillator", dt=0.01)

# 3. Stocks for position (x) and velocity (v)
x = Stock("position", initial_value=1.0)
v = Stock("velocity", initial_value=0.0)

# 4. Flows
# dx/dt = v
dx = Flow("dx", equation=v)

# dv/dt = -(k/m)x - (c/m)v
dv = Flow("dv", equation=-(k / m) * x - (c / m) * v)

# 5. Connect flows to stocks
x.add_inflow(dx)
v.add_inflow(dv)

# 6. Add all elements to the model
model.add(m, k, c, x, v, dx, dv)

# 7. Run the simulation
results = model.run(duration=10)

print(results.head(10))
print(f"\nFinal position: {results['position'].iloc[-1]:.2f}")
print(f"\nFinal velocity: {results['velocity'].iloc[-1]:.2f}")

# 8. Plot
model.plot(results, columns=["dx", "dv", "position"])
