from mead import Stock, Flow, Model, Constant

# Based on example from: https://www.iseesystems.com/resources/help/v10/Content/Reference/Integration%20methods/Euler's_method.htm
with Model("Cooling", dt=0.5) as model:

    temperature = Stock("temperature", initial_value=100)
    cooling_coef = Constant("cooling_coef", 0.5)

    # Define the flow's equation
    cooling = Flow("cooling", temperature * cooling_coef)

    temperature.add_outflow(cooling)

results = model.run(duration=8)
print(results.head(9))
model.plot(results)
