"""
Functions Demo using the new Symbolic API.
This example demonstrates how to create various types of flows using the new symbolic API.
Note: Some complex functions from the original example (e.g., smoothed, clip, table_lookup, conditional logic)
are not directly supported by basic symbolic equations and would require new Element types or helper functions.
"""

from mead import Flow, Model, Stock, Constant, Delay, Equation

# --- Helper functions for aggregation ---
def sum_elements(*elements: Element) -> Equation:
    if not elements:
        return Constant("sum_zero", 0)
    result = elements[0]
    for i in range(1, len(elements)):
        result = result + elements[i]
    return result

def min_elements(*elements: Element) -> Equation:
    # Requires a symbolic Min Element, for now simplify or handle outside the core equation
    # For demonstration, we'll just pick one or sum for simplicity if min/max not yet implemented
    raise NotImplementedError("Symbolic min_elements is not yet implemented.")

def max_elements(*elements: Element) -> Equation:
    # Requires a symbolic Max Element
    raise NotImplementedError("Symbolic max_elements is not yet implemented.")


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
# Need to create the stock *first* before using it in its own equation
_fractional_stock_instance = Stock("fractional", initial_value=1)
fractional_eq = _fractional_stock_instance * fractional_rate_val
fractional_stock = create_demo_stock("fractional", fractional_eq, initial=_fractional_stock_instance.initial_value)
model.add(fractional_rate_val) # Only add the constant here, stock already added by create_demo_stock


# --- Demo: Step function (simplified, as symbolic step not yet implemented) ---
# A symbolic step function would require conditional logic.
# For now, create a flow that is a constant, as a placeholder.
step_value = Constant("step_value", 2)
step_stock = create_demo_stock("step", step_value, initial=0)
model.add(step_value)


# --- Demo: Ramp function (simplified, as symbolic ramp not yet implemented) ---
# A symbolic ramp function would require conditional logic based on time.
# For now, create a flow that is a constant, as a placeholder.
ramp_slope = Constant("ramp_slope", 0.5)
ramp_stock = create_demo_stock("ramp", ramp_slope, initial=0)
model.add(ramp_slope)


# --- Demo: Single Pulse (simplified) ---
# Requires symbolic conditional logic based on time.
# For now, create a flow that is a constant.
pulse_value = Constant("pulse_value", 30)
pulse_stock = create_demo_stock("single_pulse", pulse_value, initial=0)
model.add(pulse_value)


# --- Demo: Smoothed (simplified) ---
# Requires new Smoothing Element. For now, constant.
smoothed_target = Constant("smoothed_target", 10)
smoothed_tau = Constant("smoothed_tau", 10) # Placeholder, not used directly in current simplified Flow
smoothed_stock = create_demo_stock("smoothed", smoothed_target, initial=40)
model.add(smoothed_target, smoothed_tau)


# --- Demo: Clip (simplified) ---
# Requires symbolic conditional logic. For now, constant.
clip_val = Constant("clip_val", 10)
clip_stock = create_demo_stock("clip", clip_val, initial=30)
model.add(clip_val)


# --- Demo: Sum of Stocks ---
# This will require all_stocks_for_sum to be Element objects.
# We need to add all stocks to the model BEFORE using them in aggregation functions.
# This approach needs to collect the stock objects themselves, not their names.
sum_stock_elements = sum_elements(*all_stocks_for_sum)
sum_flow = Flow("sum_flow", equation=sum_stock_elements)
sum_display_stock = Stock("sum_display", initial_value=0) # A stock to show the sum
sum_display_stock.add_inflow(sum_flow)
model.add(sum_display_stock, sum_flow)


# --- Demo: Min of Stocks ---
# For now, just a placeholder constant
min_stock_elements_val = Constant("min_stock_elements_val", 5)
min_flow = Flow("min_flow", equation=min_stock_elements_val)
min_display_stock = Stock("min_display", initial_value=0)
min_display_stock.add_inflow(min_flow)
model.add(min_display_stock, min_flow, min_stock_elements_val)


# --- Demo: Max of Stocks ---
# For now, just a placeholder constant
max_stock_elements_val = Constant("max_stock_elements_val", 90)
max_flow = Flow("max_flow", equation=max_stock_elements_val)
max_display_stock = Stock("max_display", initial_value=0)
max_display_stock.add_inflow(max_flow)
model.add(max_display_stock, max_flow, max_stock_elements_val)


# --- Demo: Table Lookup (simplified) ---
# Requires new Element type for Table Lookup. For now, constant.
table_lookup_val = Constant("table_lookup_val", 1.5)
table_lookup_stock = create_demo_stock("table_lookup", table_lookup_val, initial=0)
model.add(table_lookup_val)


# --- Demo: Delayed Flow ---
source_stock = Stock("source", initial_value=1)
# The delayed_val will be the value of source_stock 3 time units ago
delayed_val_eq = Delay("delayed_val_eq", input_stock=source_stock, delay_time=3.0)
target_stock_for_delay = Stock("delayed", initial_value=0)
delayed_inflow = Flow("source_to_target", equation=delayed_val_eq)
target_stock_for_delay.add_inflow(delayed_inflow)
model.add(source_stock, target_stock_for_delay, delayed_val_eq, delayed_inflow)


# Run the simulation
results = model.run(duration=20)
print(results.head(20))
