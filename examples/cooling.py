from mead import Stock, Flow, Model, Constant

# Based on example from: https://www.iseesystems.com/resources/help/v10/Content/Reference/Integration%20methods/Euler's_method.htm
dt = 0.5
cooling_coef_val = 0.5

model = Model("Cooling", dt=dt)

temperature = Stock("temperature", initial_value=100)
cooling_coef = Constant("cooling_coef", cooling_coef_val)

# Define the flow's equation symbolically
cooling_eq = temperature * cooling_coef
cooling = Flow("cooling", equation=cooling_eq)

temperature.add_outflow(cooling)
model.add(temperature, cooling_coef, cooling)

results = model.run(duration=8)

print(results.head(9))

model.plot(results)
