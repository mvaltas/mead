from mead import Model
from mead.components import Step

model = Model("Functions Demo", dt=1)

step_signal = Step("step_signal", 5, 0, 1)

model.add(step_signal)

results = model.run(duration=10)
print(results.tail(10))

model.plot(results)
