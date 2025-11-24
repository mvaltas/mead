from mead import Model
from mead.components import Pulse

time_step = 1.0
model = Model("Functions Demo", dt=time_step)

pulse_signal = Pulse("pulse_signal", start_time=4, duration=3, ammount=100)
model.add(pulse_signal)

results = model.run(duration=20)
print(results.tail(10))

model.plot(results)
