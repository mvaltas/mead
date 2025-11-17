from mead.symbols import Stock, Flow, Auxiliary, Constant, Delay, SmoothedAuxiliary
from mead.model import Model
from mead.graph import Graph

m = Model()

temp = Stock("Temperature", initial_value=70)

target_temp = Constant("Target temp", value=70)
env_temp = Constant("Environment temp", value=60)

# outflow from room to environment
temp_lost_to_env = Flow("Lost to env", formula=lambda: 0.01 * (temp.value - env_temp))

# heater power when activated
temp_heater = Constant(
    "Heater power", 
    value=1 # 1/dt -> 1 degree per dt power
)  

# signal is 1 if heater should turn on, 0 if off
heater_signal = Auxiliary(
    "Heater signal",
    formula=lambda: 1.0 if temp.value < float(target_temp) else 0.0
)

# heater takes 3 steps to react
heater_signal_delayed = Delay("Heater delay", steps=2, input=heater_signal)

# Heater takes 10 steps to full power
smoothed_heater = SmoothedAuxiliary("Heater ramp", heater_signal_delayed, tau_steps=10)

# when heater activates
heater_active = Flow(
    "Heater on",
    formula=lambda: (
        float(temp_heater) * float(smoothed_heater)
    ),
)

# connect in/out flows
temp.add_inflow(heater_active)
temp.add_outflow(temp_lost_to_env)

m.add_stock(temp)

history = m.run(steps=360, dt=1)

#history["heater_on"] = [h * 1 for h in heater_active.history]

Graph().plot(history)
