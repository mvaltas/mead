from mead import Stock, Flow, Model, constant

# Example from: https://www.iseesystems.com/resources/help/v10/Content/Reference/Integration%20methods/Euler's_method.htm
# comparing with our solution

dt = 0.5
cooling_coef = 0.5


model = Model("Cooling", dt=0.50)

temperature = Stock("temperature", initial_value=100)

cooling = Flow("cooling", equation=lambda t,s: s["temperature"] * cooling_coef)

temperature.add_outflow(cooling)

model.add_stock(temperature)

results = model.run(duration=8)

results["cooling"] = results["temperature"] * cooling_coef * dt

print(results.head(9))

model.plot(results, "temperature", "cooling")
