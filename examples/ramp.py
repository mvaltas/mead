from mead import Model
from mead.components import Ramp

time_step = 1.0
model = Model("Functions Demo", dt=time_step)

ramp_signal = Ramp(name="ramp_signal", start_time=6, end_time=12, ammount=2)
model.add(ramp_signal)

results = model.run(duration=20)
print(results.tail(10))

model.plot(results)
