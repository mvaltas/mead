"""
Illustrates the use of the Delay2 component, which simulates a second-order
exponential delay.

This example sets up a simple model where a Step input is fed into Delay2, Delay3,
and a first-order Smooth component. The outputs should show characteristic
delayed and S-shaped responses, with Delay2 being less delayed and less S-shaped
than Delay3, but more so than the first-order Smooth.
"""

import matplotlib.pyplot as plt

from mead.core import Constant
from mead.model import Model
from mead.components import Delay2, Delay3, Step, Smooth


model = Model(name="Delay2 Example Model", dt=0.125)

# Define an input step function
step_input = Step(
    name="Step Input",
    start_time=Constant("Step Start Time", 10.0),
    before_value=Constant("Before Step Value", 0.0),
    after_value=Constant("After Step Value", 100.0)
)

# Define a Delay2 component
delay_time = Constant("Delay Time", 5.0)  # Total delay time
delayed_output_2 = Delay2(
    name="Delayed Output (2nd Order)",
    input_element=step_input,
    delay_time=delay_time,
    initial_value=Constant("Initial Delayed Value 2", 0.0)
)

# For comparison, also include Delay3
delayed_output_3 = Delay3(
    name="Delayed Output (3rd Order)",
    input_element=step_input,
    delay_time=delay_time,
    initial_value=Constant("Initial Delayed Value 3", 0.0)
)

# For comparison, also include a first-order smooth
smooth_output = Smooth(
    name="Smooth Output (1st Order)",
    target_value=step_input,
    smoothing_time=Constant("Smoothing Time (1st Order)", 5.0), # Same time constant for comparison
    initial_value=Constant("Initial Smooth Value", 0.0)
)

# Add elements to the model
model.add(step_input, delayed_output_2, delayed_output_3, smooth_output)

# Simulation duration
duration = 30.0

# Run the simulation
results = model.run(duration=duration)

# Plotting the results
time_points = results.index
step_input_values = results["Step Input"]
delayed_output_2_values = results["Delayed Output (2nd Order)"]
delayed_output_3_values = results["Delayed Output (3rd Order)"]
smooth_output_values = results["Smooth Output (1st Order)"]

plt.figure(figsize=(12, 6))
plt.plot(time_points, step_input_values, label="Step Input", linestyle='--', color='blue')
plt.plot(time_points, delayed_output_2_values, label="Delayed Output (2nd Order)", color='orange')
plt.plot(time_points, delayed_output_3_values, label="Delayed Output (3rd Order)", color='red')
plt.plot(time_points, smooth_output_values, label="Smooth Output (1st Order)", color='green')

plt.title("Delay2 Component Demonstration")
plt.xlabel("Time")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.show()

print("Delay2 example simulation completed.")
