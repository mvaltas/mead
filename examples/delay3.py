"""
Illustrates the use of the Delay3 component, which simulates a third-order
exponential delay.

This example sets up a simple model where a Step input is fed into a Delay3
component. The output of the Delay3 should show a characteristic S-shaped
response, delayed relative to the input step.
"""
from mead.core import Constant
from mead.model import Model
from mead.components import Delay3, Step, Smooth


model = Model(name="Delay3 Example Model", dt=0.125)

step_input = Step(
    name="Step Input",
    start_time=Constant("Step Start Time", 10.0),
    before_value=Constant("Before Step Value", 0.0),
    after_value=Constant("After Step Value", 100.0)
)


delay_time = Constant("Delay Time", 5.0)
delayed_output_3 = Delay3(
    name="Delayed Output (3rd Order)",
    input_element=step_input,
    delay_time=delay_time,
    initial_value=Constant("Initial Delayed Value", 0.0)
)

# For comparison 
smooth_output = Smooth(
    name="Smooth Output (1st Order)",
    target_value=step_input,
    smoothing_time=Constant("Smoothing Time (1st Order)", 5.0),
    initial_value=Constant("Initial Smooth Value", 0.0)
)

model.add(step_input, delayed_output_3, smooth_output)

results = model.run(duration=30.0)

print(results.tail(10))

model.plot(results, columns = [
    'Step Input', 
    'Delayed Output (3rd Order)', 
    'Smooth Output (1st Order)'])
