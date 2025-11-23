from mead import Flow, Model, Stock, Constant, Equation, Auxiliary
from mead.components import Delay, Smooth, Table, Min, Max, Pulse, Step, Ramp, IfThenElse, Initial

# Model setup
time_step = 1.0 # Use float for dt
model = Model("Functions Demo", dt=time_step)

# --- Demo: Ramp function ---
# Goal: Show a value increasing linearly over a period
ramp_start_time = Constant("ramp_start_time", 2.0)
ramp_end_time = Constant("ramp_end_time", 8.0)
ramp_slope = Constant("ramp_slope", 5.0)
ramp_initial_val = Constant("ramp_initial_val", 0.0)
ramp_signal = Ramp("ramp_signal", ramp_start_time, ramp_end_time, ramp_slope, ramp_initial_val)
model.add(ramp_start_time, ramp_end_time, ramp_slope, ramp_initial_val, ramp_signal)


## --- Demo: Pulse function ---
## Goal: Show a temporary burst of value
#pulse_start_time = Constant("pulse_start_time", 4.0)
#pulse_duration = Constant("pulse_duration", 3.0)
#pulse_magnitude = Constant("pulse_magnitude", 100.0)
#pulse_signal = Pulse("pulse_signal", pulse_start_time, pulse_duration, pulse_magnitude)
#model.add(pulse_start_time, pulse_duration, pulse_magnitude, pulse_signal)
#
#
## --- Demo: Smoothed (First Order Exponential Smooth) ---
## Goal: Show a value lagging and dampening changes in its input
#input_for_smooth = Stock("input_for_smooth", initial_value=0.0)
#input_for_smooth_step_start = Constant("input_for_smooth_step_start", 5.0)
#input_for_smooth_step_before = Constant("input_for_smooth_step_before", 0.0)
#input_for_smooth_step_after = Constant("input_for_smooth_step_after", 100.0)
#input_for_smooth_flow_source = Step("input_for_smooth_flow_source", 
#                                    input_for_smooth_step_start, input_for_smooth_step_before, input_for_smooth_step_after)
#input_for_smooth_flow = Flow("input_for_smooth_flow", input_for_smooth_flow_source)
#input_for_smooth.add_inflow(input_for_smooth_flow)
#
#smoothing_time = Constant("smoothing_time", 10.0) # Longer smoothing time for clearer effect
#smoothed_output = Smooth("smoothed_output", input_for_smooth, smoothing_time, initial_value=0.0)
#model.add(input_for_smooth, input_for_smooth_flow_source, input_for_smooth_flow,
#          input_for_smooth_step_start, input_for_smooth_step_before, input_for_smooth_step_after,
#          smoothing_time, smoothed_output)
#
#
## --- Demo: Table Lookup ---
## Goal: Show non-linear functional relationship
#table_input_val = Stock("table_input_val", initial_value=0.0)
#table_input_flow_rate = Constant("table_input_flow_rate", 0.5)
#table_input_flow = Flow("table_input_flow", table_input_flow_rate)
#table_input_val.add_inflow(table_input_flow)
#
#table_points = [(0,0), (5,50), (10,100), (15,50), (20,0)] # Example non-linear relationship
#table_output = Table("table_output", table_input_val, table_points)
#model.add(table_input_val, table_input_flow_rate, table_input_flow, table_output)
#
#
## --- Demo: IfThenElse (Conditional Logic) ---
## Goal: Show switching behavior based on a condition
#conditional_input = Stock("conditional_input", initial_value=20.0)
#conditional_input_flow_rate = Constant("conditional_input_flow_rate", -2.0)
#conditional_input_flow = Flow("conditional_input_flow", conditional_input_flow_rate)
#conditional_input.add_inflow(conditional_input_flow)
#
#threshold_val = Constant("threshold_val", 10.0)
#true_val = Constant("true_val", 100.0)
#false_val = Constant("false_val", 0.0)
#
#condition_eq = conditional_input - threshold_val # Condition: conditional_input > threshold_val (i.e., this eq > 0)
#conditional_output = IfThenElse("conditional_output", condition_eq, true_val, false_val)
#model.add(conditional_input, conditional_input_flow_rate, conditional_input_flow,
#          threshold_val, true_val, false_val, condition_eq, conditional_output)
#
#
## --- Demo: Min and Max ---
## Goal: Show selection of min/max values dynamically
#min_max_input1 = Constant("min_max_input1", 20.0)
#min_max_input2 = Stock("min_max_input2", initial_value=5.0)
#min_max_input3 = Constant("min_max_input3", 30.0)
#
#min_max_input2_flow_rate = Constant("min_max_input2_flow_rate", 5.0) # Make input2 increase
#min_max_input2_flow = Flow("min_max_input2_flow", min_max_input2_flow_rate)
#min_max_input2.add_inflow(min_max_input2_flow)
#
#min_output = Min("min_output", min_max_input1, min_max_input2, min_max_input3)
#max_output = Max("max_output", min_max_input1, min_max_input2, min_max_input3)
#model.add(min_max_input1, min_max_input2, min_max_input3,
#          min_max_input2_flow_rate, min_max_input2_flow,
#          min_output, max_output)
#
#
## --- Demo: Initial ---
## Goal: Show how to access initial value of a stock
#stock_with_initial = Stock("stock_with_initial", initial_value=75.0)
#initial_value_output = Initial("initial_value_output", stock_with_initial)
#model.add(stock_with_initial, initial_value_output)
#
#
## --- Demo: Delayed Flow (from previous example) ---
## Goal: Show a value from a stock delayed in time
#source_stock = Stock("source_stock", initial_value=1.0)
#source_stock_flow_rate = Constant("source_stock_flow_rate", 1.0)
#source_stock_flow = Flow("source_stock_flow", source_stock_flow_rate)
#source_stock.add_inflow(source_stock_flow)
#
#delay_time = Constant("delay_time", 3.0)
#delayed_output = Delay("delayed_output", source_stock, delay_time)
#model.add(source_stock, source_stock_flow_rate, source_stock_flow, delay_time, delayed_output)


# Run the simulation
results = model.run(duration=20)
print(results.tail(10))

# Plotting selected key results
model.plot(results,
    columns = [
        "ramp_signal",
    ],
)
