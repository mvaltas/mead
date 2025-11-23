"""
Functions Demo using the new Symbolic API.
This example demonstrates how to create various types of flows using the new symbolic API.
"""

from mead import Flow, Model, Stock, Constant, Equation, Auxiliary # Auxiliary might be useful for intermediate steps
from mead.components import Delay, Smooth, Table, Min, Max, Pulse, Step, Ramp # Import all new specialized components

# --- Helper functions for aggregation (Min/Max now handled by components) ---
def sum_elements(*elements: Element) -> Equation:
    if not elements:
        return Constant("sum_zero", 0)
    result = elements[0]
    for i in range(1, len(elements)):
        result = result + elements[i]
    return result

# Old min_elements/max_elements removed, replaced by Min/Max components

time_step = 1
model = Model("Functions Demo", dt=time_step)

all_stocks_for_sum = [] # To collect stocks for sum_elements demo

def create_demo_stock(name: str, equation: Element, initial: float = 0):
    stock = Stock(name, initial_value=initial)
    flow = Flow(f"inflow_{name}", equation=equation)
    stock.add_inflow(flow)
    model.add(stock, flow) # Add both stock and flow to model
    all_stocks_for_sum.append(stock) # Collect for aggregation demos
    return stock

# --- Demo: Fractional (Exponential Growth) ---
fractional_rate_val = Constant("fractional_rate", 0.2)
_fractional_stock_instance = Stock("fractional", initial_value=1)
fractional_eq = _fractional_stock_instance * fractional_rate_val
fractional_stock = create_demo_stock("fractional", fractional_eq, initial=_fractional_stock_instance.initial_value)
model.add(fractional_rate_val) # _fractional_stock_instance is added by create_demo_stock


# --- Demo: Step function ---
step_start_time = Constant("step_start_time", 5)
step_before_val = Constant("step_before_val", 1)
step_after_val = Constant("step_after_val", 10)
step_component = Step("step_val", step_start_time, step_before_val, step_after_val)
step_stock = create_demo_stock("step_stock", step_component, initial=0) # Stock accumulating the step output
model.add(step_start_time, step_before_val, step_after_val, step_component)


# --- Demo: Ramp function ---
ramp_start_time = Constant("ramp_start_time", 2)
ramp_end_time = Constant("ramp_end_time", 8)
ramp_slope = Constant("ramp_slope", 2)
ramp_initial_val = Constant("ramp_initial_val", 0)
ramp_component = Ramp("ramp_val", ramp_start_time, ramp_end_time, ramp_slope, ramp_initial_val)
ramp_stock = create_demo_stock("ramp_stock", ramp_component, initial=0) # Stock accumulating the ramp output
model.add(ramp_start_time, ramp_end_time, ramp_slope, ramp_initial_val, ramp_component)


# --- Demo: Single Pulse ---
pulse_start_time = Constant("pulse_start_time", 4)
pulse_duration = Constant("pulse_duration", 3)
pulse_magnitude = Constant("pulse_magnitude", 50)
pulse_component = Pulse("pulse_val", pulse_start_time, pulse_duration, pulse_magnitude)
pulse_stock = create_demo_stock("pulse_stock", pulse_component, initial=0) # Stock accumulating the pulse output
model.add(pulse_start_time, pulse_duration, pulse_magnitude, pulse_component)


# --- Demo: Smoothed ---
smoothed_input = Stock("smoothed_input", 10) # A stock to provide varying input
smoothed_input_flow = Flow("smoothed_input_flow", Constant("smoothed_input_rate", 5)) # Increases by 5 each step
smoothed_input.add_inflow(smoothed_input_flow)

smoothing_time_const = Constant("smoothing_time", 3)
smoothed_component = Smooth("smoothed_val", smoothed_input, smoothing_time_const, initial_value=smoothed_input.initial_value)
smoothed_output_stock = create_demo_stock("smoothed_output_stock", smoothed_component, initial=0) # Accumulate smooth output
model.add(smoothed_input, smoothed_input_flow, smoothing_time_const, smoothed_component)


# --- Demo: Clip (still simplified, full clip requires IfThenElse) ---
# A true clip would be: IfThenElse(input_val > upper, upper, IfThenElse(input_val < lower, lower, input_val))
# For now, let's just make it a constant + stock as a placeholder, not using IfThenElse yet
clip_input = Stock("clip_input", 10)
clip_input_flow = Flow("clip_input_flow", Constant("clip_input_rate", 2))
clip_input.add_inflow(clip_input_flow)
clip_output = Auxiliary("clip_output", clip_input) # For now, just passes through
model.add(clip_input, clip_input_flow, clip_output)


# --- Demo: Sum of Stocks ---
# This will require all_stocks_for_sum to be Element objects.
# We need to add all stocks to the model BEFORE using them in aggregation functions.
sum_stock_elements = sum_elements(*all_stocks_for_sum)
sum_flow = Flow("sum_flow", equation=sum_stock_elements)
sum_display_stock = Stock("sum_display", initial_value=0) # A stock to show the sum
sum_display_stock.add_inflow(sum_flow)
model.add(sum_display_stock, sum_flow)


# --- Demo: Min of Stocks ---
# Using the new Min component
min_input1 = Constant("min_input1", 10)
min_input2 = Stock("min_input2", 20)
min_input2_flow = Flow("min_input2_flow", Constant("min_input2_rate", -2)) # Decreasing
min_input2.add_inflow(min_input2_flow)
min_component = Min("min_val", min_input1, min_input2, Constant("min_input3", 5))
min_output_stock = create_demo_stock("min_output_stock", min_component, initial=0) # Accumulate min output
model.add(min_input1, min_input2, min_input2_flow, min_component, Constant("min_input3", 5))


# --- Demo: Max of Stocks ---
# Using the new Max component
max_input1 = Constant("max_input1", 10)
max_input2 = Stock("max_input2", 5)
max_input2_flow = Flow("max_input2_flow", Constant("max_input2_rate", 3)) # Increasing
max_input2.add_inflow(max_input2_flow)
max_component = Max("max_val", max_input1, max_input2, Constant("max_input3", 15))
max_output_stock = create_demo_stock("max_output_stock", max_component, initial=0) # Accumulate max output
model.add(max_input1, max_input2, max_input2_flow, max_component, Constant("max_input3", 15))


# --- Demo: Table Lookup ---
table_input = Stock("table_input", 0)
table_input_flow = Flow("table_input_flow", Constant("table_input_rate", 0.5)) # Input grows by 0.5 per step
table_input.add_inflow(table_input_flow)

table_points = [(0,0), (10,100), (20,50), (30,0)] # x-values, y-values
table_component = Table("table_lookup_val", table_input, table_points)
table_output_stock = create_demo_stock("table_output_stock", table_component, initial=0) # Accumulate table output
model.add(table_input, table_input_flow, table_component)


# --- Demo: Delayed Flow ---
source_stock = Stock("source", initial_value=1)
# The delayed_val will be the value of source_stock 3 time units ago
delayed_val_eq = Delay("delayed_val_eq", input_stock=source_stock, delay_time=3.0)
target_stock_for_delay = Stock("delayed_stock", initial_value=0) # Changed name to avoid conflict with 'delayed' in results
delayed_inflow = Flow("source_to_target", equation=delayed_val_eq)
target_stock_for_delay.add_inflow(delayed_inflow)
model.add(source_stock, target_stock_for_delay, delayed_val_eq, delayed_inflow)


# Run the simulation
results = model.run(duration=20)
print(results.head(20))
