"""
Illustrates the use of the Delay2 component, which simulates a second-order
exponential delay.

This example sets up a simple model where a Step input is fed into Delay2, Delay3,
and a first-order Smooth component. The outputs should show characteristic
delayed and S-shaped responses, with Delay2 being less delayed and less S-shaped
than Delay3, but more so than the first-order Smooth.
"""

from mead.core import Constant
from mead.model import Model
from mead.components import Delay, Delay2, Delay3, Step, Smooth

with Model(name="Delay2 Example Model", dt=0.125) as model:
    # Define an input step function
    step_input = Step(
        name="Step Input",
        start_time=Constant("Step Start Time", 10.0),
        before_value=Constant("Before Step Value", 0.0),
        after_value=Constant("After Step Value", 100.0),
    )


    # Simple delay just holds for N steps, no smoothing
    delay = Delay(
            name="Delay", 
            input_stock=step_input, 
            delay_time = 3.0
    )

    # Define a Delay2 component
    delay_time = Constant("Delay Time", 5.0)  # Total delay time
    delayed_output_2 = Delay2(
        name="Delayed Output (2nd Order)",
        input_element=step_input,
        delay_time=delay_time,
        initial_value=Constant("Initial Delayed Value 2", 0.0),
    )

    # For comparison, also include Delay3
    delayed_output_3 = Delay3(
        name="Delayed Output (3rd Order)",
        input_element=step_input,
        delay_time=delay_time,
        initial_value=Constant("Initial Delayed Value 3", 0.0),
    )

    # For comparison, also include a first-order smooth
    smooth_output = Smooth(
        name="Smooth Output (1st Order)",
        target_value=step_input,
        smoothing_time=Constant(
            "Smoothing Time (1st Order)", 5.0
        ),  # Same time constant for comparison
        initial_value=Constant("Initial Smooth Value", 0.0),
    )

# Run the simulation
results = model.run(duration=30.0)

# Plotting the results using model.plot
model.plot(results, columns=[
    'Step Input',
    'Delay',
    'Delayed Output (2nd Order)',
    'Delayed Output (3rd Order)',
    'Smooth Output (1st Order)',
    ])
