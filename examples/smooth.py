from mead import Model
from mead.components import Smooth

time_step = 1.0
model = Model("Functions Demo", dt=time_step)

smoothed_output = Smooth(
    "smoothed_output", target_value=30, smoothing_time=10, initial_value=50
)
model.add(smoothed_output)

results = model.run(duration=20)
print(results.tail(10))

model.plot(results, columns=["smoothed_output"])
