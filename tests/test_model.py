from mead.core import Constant
from mead.components import Hold  # Import Delay from its new location
from mead.stock import Stock
from mead.flow import Flow
from mead.model import Model
import pytest

# Dummy context for testing elements in isolation within tests
dummy_context_model = {
    "state": {"population": 100, "input_stock": 10, "other": 50},
    "time": 0.0,
    "history_lookup": lambda name, delay_time: 123.0,  # A simple, constant return for testing
}


def test_model_add_elements():
    model = Model("test")
    p = Stock("population", 100)
    br = Constant("birth_rate", 0.1)
    model.add(p, br)
    assert "population" in model.elements
    assert "birth_rate" in model.elements
    assert "population" in model.stocks


def test_exponential_growth_euler():
    model = Model("growth", dt=1.0)

    population = Stock("population", 100)
    birth_rate = Constant("birth_rate", 0.1)

    # Equation is defined symbolically
    births_eq = population * birth_rate
    births = Flow("births", equation=births_eq)

    population.add_inflow(births)

    model.add(population, birth_rate, births)

    results = model.run(duration=3)

    # Check results
    assert results.loc[0, "population"] == 100
    # t=1: 100 + (100 * 0.1) * 1.0 = 110
    assert results.loc[1, "population"] == pytest.approx(110)
    # t=2: 110 + (110 * 0.1) * 1.0 = 121
    assert results.loc[2, "population"] == pytest.approx(121)
    # t=3: 121 + (121 * 0.1) * 1.0 = 133.1
    assert results.loc[3, "population"] == pytest.approx(133.1)


def test_goal_seeking_model():
    model = Model("goal_seek", dt=1.0)

    target_val = Constant("target_val", 1000)
    inventory = Stock("inventory", 100)
    adj_time = Constant("adjustment_time", 4)

    # gap = target - inventory
    gap = target_val - inventory
    # adjustment = gap / adjustment_time
    adjustment_eq = gap / adj_time

    adjustment_flow = Flow("adjustment", equation=adjustment_eq)
    inventory.add_inflow(adjustment_flow)

    model.add(inventory, target_val, adj_time, adjustment_flow, gap)

    results = model.run(duration=10)

    # Check that inventory moves towards target
    assert results["inventory"].iloc[0] == 100
    assert results["inventory"].iloc[1] > 100
    # The calculated final value for dt=1, duration=10, initial=100, target=1000, adj_time=4
    assert results["inventory"].iloc[-1] == pytest.approx(949.3178367614746)


def test_delay_element_in_model():
    model = Model("delay_test", dt=1.0)

    input_stock = Stock("input_stock", 50)
    constant_rate = Constant("constant_rate", 10)

    # Inflow to input_stock is a constant rate
    input_flow = Flow("input_flow", constant_rate)
    input_stock.add_inflow(input_flow)

    # Delayed value of input_stock
    delayed_val = Hold(
        "delayed_val", input_stock, Constant("time_units", 3.0)
    )  # Delay by 3 time units

    # Output stock receives the delayed value
    output_stock = Stock("output_stock", 0)
    output_flow = Flow("output_flow", delayed_val)
    output_stock.add_inflow(output_flow)

    model.add(
        input_stock, constant_rate, input_flow, delayed_val, output_stock, output_flow
    )

    results = model.run(duration=5)

    # input_stock will be 50, 60, 70, 80, 90, 100 at the start of each step
    assert results.loc[0, "input_stock"] == 50
    assert results.loc[1, "input_stock"] == 60
    assert results.loc[2, "input_stock"] == 70
    assert results.loc[3, "input_stock"] == 80
    assert results.loc[4, "input_stock"] == 90
    assert results.loc[5, "input_stock"] == 100

    # output_stock accumulates the delayed input_stock values
    # delayed_val is 0 for t=0,1,2 (delay time = 3)
    # At t=3, delayed_val gets value from input_stock at t=0 (50) -> inflow = 50. output_stock for t=3 is 0.
    # At t=4, delayed_val gets value from input_stock at t=1 (60) -> inflow = 60. output_stock for t=4 is 50.
    # At t=5, delayed_val gets value from input_stock at t=2 (70) -> inflow = 70. output_stock for t=5 is 50+60=110.

    assert results.loc[0, "output_stock"] == 0
    assert results.loc[1, "output_stock"] == 0
    assert results.loc[2, "output_stock"] == 0
    assert (
        results.loc[3, "output_stock"] == 0
    )  # At start of t=3, output_stock is still 0
    assert results.loc[4, "output_stock"] == pytest.approx(
        50
    )  # At start of t=4, output_stock has accumulated 50 from t=3
    assert results.loc[5, "output_stock"] == pytest.approx(
        50 + 60
    )  # At start of t=5, output_stock has accumulated 50+60 from t=3, t=4


def test_smooth_element_in_model():
    from mead.components import Smooth  # Import Smooth for this test

    model = Model("smooth_test", dt=1.0)

    input_element = Stock("input_element", 100)  # Input will increase by 10 each step
    input_flow = Flow("input_flow", Constant("input_rate", 10))
    input_element.add_inflow(input_flow)

    smoothing_time = Constant("smoothing_time", 2.0)  # 2.0 time units for smoothing
    smooth_val = Smooth(
        "smooth_val",
        input_element,
        smoothing_time,
        initial_value=input_element.initial_value,
    )

    model.add(input_element, input_flow, smoothing_time, smooth_val)

    results = model.run(duration=5)

    # Expected values for input_element: 100, 110, 120, 130, 140, 150
    # Expected values for smooth_val (initial_value=100, smoothing_time=2.0, dt=1.0)
    # t=0: smooth_val = 100 (initial)
    # t=1: 100 + (1/2)*(110-100) = 100 + 5 = 105
    # t=2: 105 + (1/2)*(120-105) = 105 + 7.5 = 112.5
    # t=3: 112.5 + (1/2)*(130-112.5) = 112.5 + 8.75 = 121.25
    # t=4: 121.25 + (1/2)*(140-121.25) = 121.25 + 9.375 = 130.625
    # t=5: 130.625 + (1/2)*(150-130.625) = 130.625 + 9.6875 = 140.3125

    assert results.loc[0, "smooth_val"] == pytest.approx(100)
    assert results.loc[1, "smooth_val"] == pytest.approx(105)
    assert results.loc[2, "smooth_val"] == pytest.approx(112.5)
    assert results.loc[3, "smooth_val"] == pytest.approx(121.25)
    assert results.loc[4, "smooth_val"] == pytest.approx(130.625)
    assert results.loc[5, "smooth_val"] == pytest.approx(140.3125)


def test_table_element_in_model():
    from mead.components import Table  # Import Table for this test

    model = Model("table_test", dt=1.0)

    input_for_table = Stock("input_for_table", 0)  # This will increase by 1 each step
    input_flow = Flow("input_flow", Constant("input_rate", 1))
    input_for_table.add_inflow(input_flow)

    # Define a simple table: (x, y) points
    # (0, 0), (1, 10), (2, 20), (3, 10), (4, 0)
    # This creates a ramp up then ramp down shape
    table_points = [(0.0, 0.0), (1.0, 10.0), (2.0, 20.0), (3.0, 10.0), (4.0, 0.0)]
    table_lookup = Table("table_lookup_val", input_for_table, table_points)

    model.add(input_for_table, input_flow, table_lookup)

    results = model.run(duration=5)

    # Expected input_for_table values: 0, 1, 2, 3, 4, 5
    # Expected table_lookup_val:
    # t=0: input=0, output=0 (extrapolation)
    # t=1: input=1, output=10 (exact point)
    # t=2: input=2, output=20 (exact point)
    # t=3: input=3, output=10 (exact point)
    # t=4: input=4, output=0 (exact point)
    # t=5: input=5, output=0 (extrapolation)

    assert results.loc[0, "table_lookup_val"] == pytest.approx(0.0)
    assert results.loc[1, "table_lookup_val"] == pytest.approx(10.0)
    assert results.loc[2, "table_lookup_val"] == pytest.approx(20.0)
    assert results.loc[3, "table_lookup_val"] == pytest.approx(10.0)
    assert results.loc[4, "table_lookup_val"] == pytest.approx(0.0)
    assert results.loc[5, "table_lookup_val"] == pytest.approx(0.0)  # Extrapolation

    # Test interpolation at t=0.5 (need to re-run model with smaller dt or check mid-step)
    # For now, rely on point and extrapolation checks
    # To test interpolation at say, input_for_table = 0.5, need to set initial_value differently or change dt.

    # Let's add a quick check for interpolation using a Constant as input
    model_interp = Model("table_interp_test", dt=1.0)
    interp_input = Constant("interp_input", 1.5)  # Value between 1 and 2
    interp_table = Table("interp_table_val", interp_input, table_points)
    model_interp.add(interp_input, interp_table)
    interp_results = model_interp.run(duration=0)  # Run for 1 step to get initial value
    # For input 1.5:
    # x1=1, y1=10
    # x2=2, y2=20
    # y = 10 + (1.5 - 1) * (20 - 10) / (2 - 1) = 10 + 0.5 * 10 / 1 = 10 + 5 = 15
    assert interp_results.loc[0, "interp_table_val"] == pytest.approx(15.0)


def test_ifthenelse_element_in_model():
    from mead.components import IfThenElse  # Import IfThenElse for this test

    model = Model("ifthenelse_test", dt=1.0)

    # Elements for the IfThenElse
    input_val = Stock("input_val", initial_value=5)
    threshold = Constant("threshold", 10)
    true_output = Constant("true_output", 100)
    false_output = Constant("false_output", 50)

    # Condition: input_val > threshold
    condition_eq = input_val - threshold  # Will be > 0 if input_val > threshold
    conditional_val = IfThenElse(
        "conditional_val", condition_eq, true_output, false_output
    )

    # A flow to change input_val so condition switches
    input_flow_rate = Constant("input_flow_rate", 3)
    input_flow = Flow("input_flow", input_flow_rate)
    input_val.add_inflow(input_flow)

    model.add(
        input_val,
        threshold,
        true_output,
        false_output,
        condition_eq,
        conditional_val,
        input_flow_rate,
        input_flow,
    )

    results = model.run(duration=5)

    # Expected input_val: 5, 8, 11, 14, 17, 20
    # Expected condition_eq: -5, -2, 1, 4, 7, 10
    # Expected conditional_val:
    # t=0: input=5, condition=-5 (<=0), output=50
    # t=1: input=8, condition=-2 (<=0), output=50
    # t=2: input=11, condition=1 (>0), output=100
    # t=3: input=14, condition=4 (>0), output=100
    # t=4: input=17, condition=7 (>0), output=100
    # t=5: input=20, condition=10 (>0), output=100

    assert results.loc[0, "conditional_val"] == pytest.approx(50)
    assert results.loc[1, "conditional_val"] == pytest.approx(50)
    assert results.loc[2, "conditional_val"] == pytest.approx(100)
    assert results.loc[3, "conditional_val"] == pytest.approx(100)
    assert results.loc[4, "conditional_val"] == pytest.approx(100)
    assert results.loc[5, "conditional_val"] == pytest.approx(100)


def test_min_element_in_model():
    from mead.components import Min  # Import Min for this test

    model = Model("min_test", dt=1.0)

    val1 = Constant("val1", 10)
    val2 = Stock("val2", initial_value=20)
    val3 = Constant("val3", 5)

    # val2 will decrease over time to test min dynamically
    outflow_val2 = Flow("outflow_val2", Constant("out_rate", 8))
    val2.add_outflow(outflow_val2)

    min_val = Min("min_val", val1, val2, val3)

    model.add(val1, val2, val3, outflow_val2, min_val)

    results = model.run(duration=3)

    # Expected val2: 20, 12, 4, -4
    # Expected min_val:
    # t=0: min(10, 20, 5) = 5
    # t=1: min(10, 12, 5) = 5
    # t=2: min(10, 4, 5) = 4
    # t=3: min(10, -4, 5) = -4

    assert results.loc[0, "min_val"] == pytest.approx(5)
    assert results.loc[1, "min_val"] == pytest.approx(5)
    assert results.loc[2, "min_val"] == pytest.approx(4)
    assert results.loc[3, "min_val"] == pytest.approx(-4)


def test_max_element_in_model():
    from mead.components import Max  # Import Max for this test

    model = Model("max_test", dt=1.0)

    val1 = Constant("val1", 10)
    val2 = Stock("val2", initial_value=5)
    val3 = Constant("val3", 15)

    # val2 will increase over time to test max dynamically
    inflow_val2 = Flow("inflow_val2", Constant("in_rate", 8))
    val2.add_inflow(inflow_val2)

    max_val = Max("max_val", val1, val2, val3)

    model.add(val1, val2, val3, inflow_val2, max_val)

    results = model.run(duration=3)

    # Expected val2: 5, 13, 21, 29
    # Expected max_val:
    # t=0: max(10, 5, 15) = 15
    # t=1: max(10, 13, 15) = 15
    # t=2: max(10, 21, 15) = 21
    # t=3: max(10, 29, 15) = 29

    assert results.loc[0, "max_val"] == pytest.approx(15)
    assert results.loc[1, "max_val"] == pytest.approx(15)
    assert results.loc[2, "max_val"] == pytest.approx(21)
    assert results.loc[3, "max_val"] == pytest.approx(29)


def test_pulse_element_in_model():
    from mead.components import Pulse  # Import Pulse for this test

    model = Model("pulse_test", dt=1.0)

    start = Constant("start_time", 2)
    duration = Constant("duration", 2)
    mag = Constant("magnitude", 100)

    pulse_output = Pulse("pulse_output", start, duration, mag)
    model.add(start, duration, mag, pulse_output)

    results = model.run(duration=5)

    # Expected pulse_output:
    # t=0: 0
    # t=1: 0
    # t=2: 100 (start_time)
    # t=3: 100
    # t=4: 0 (start_time + duration = 4)
    # t=5: 0

    assert results.loc[0, "pulse_output"] == pytest.approx(0)
    assert results.loc[1, "pulse_output"] == pytest.approx(0)
    assert results.loc[2, "pulse_output"] == pytest.approx(100)
    assert results.loc[3, "pulse_output"] == pytest.approx(100)
    assert results.loc[4, "pulse_output"] == pytest.approx(0)
    assert results.loc[5, "pulse_output"] == pytest.approx(0)


def test_step_element_in_model():
    from mead.components import Step  # Import Step for this test

    model = Model("step_test", dt=1.0)

    start = Constant("start_time", 2)
    before = Constant("before_val", 10)
    after = Constant("after_val", 50)

    step_output = Step("step_output", start, before, after)
    model.add(start, before, after, step_output)

    results = model.run(duration=5)

    # Expected step_output:
    # t=0: 10
    # t=1: 10
    # t=2: 50 (start_time)
    # t=3: 50
    # t=4: 50
    # t=5: 50

    assert results.loc[0, "step_output"] == pytest.approx(10)
    assert results.loc[1, "step_output"] == pytest.approx(10)
    assert results.loc[2, "step_output"] == pytest.approx(50)
    assert results.loc[3, "step_output"] == pytest.approx(50)
    assert results.loc[4, "step_output"] == pytest.approx(50)
    assert results.loc[5, "step_output"] == pytest.approx(50)


def test_ramp_element_in_model():
    from mead.components import Ramp  # Import Ramp for this test

    model = Model("ramp_test", dt=1.0)

    start = Constant("start_time", 1)
    end = Constant("end_time", 4)
    slope = Constant("slope", 10)
    initial = Constant("initial_val", 5)

    ramp_output = Ramp("ramp_output", start, end, slope, initial)
    model.add(start, end, slope, initial, ramp_output)

    results = model.run(duration=6)

    # Expected ramp_output:
    # t=0: 5 (initial before start_time)
    # t=1: 5 + 10*(1-1) = 5 (start_time)
    # t=2: 5 + 10*(2-1) = 15
    # t=3: 5 + 10*(3-1) = 25
    # t=4: 5 + 10*(4-1) = 35 (end_time)
    # t=5: 35 (holds value after end_time)
    # t=6: 35

    assert results.loc[0, "ramp_output"] == pytest.approx(5)
    assert results.loc[1, "ramp_output"] == pytest.approx(5)
    assert results.loc[2, "ramp_output"] == pytest.approx(15)
    assert results.loc[3, "ramp_output"] == pytest.approx(25)
    assert results.loc[4, "ramp_output"] == pytest.approx(35)
    assert results.loc[5, "ramp_output"] == pytest.approx(35)
    assert results.loc[6, "ramp_output"] == pytest.approx(35)


import os  # Import os for file cleanup
from pathlib import Path  # Import Path for file operations


def test_initial_element_in_model():
    from mead.components import Initial  # Import Initial for this test

    model = Model("initial_test", dt=1.0)

    my_stock = Stock("my_stock", initial_value=100)
    my_constant = Constant("my_constant", 50)

    # Initial value of the stock
    initial_stock_val = Initial("initial_stock_val", my_stock)

    # Initial value of the constant (should just be its value)
    initial_constant_val = Initial("initial_constant_val", my_constant)

    # Add a flow to change my_stock
    flow_rate = Constant("flow_rate", 10)
    my_flow = Flow("my_flow", flow_rate)
    my_stock.add_inflow(my_flow)

    model.add(
        my_stock,
        my_constant,
        flow_rate,
        my_flow,
        initial_stock_val,
        initial_constant_val,
    )

    results = model.run(duration=2)

    # my_stock will be 100, 110, 120
    # initial_stock_val should always be 100
    # initial_constant_val should always be 50

    assert results.loc[0, "initial_stock_val"] == pytest.approx(100)
    assert results.loc[1, "initial_stock_val"] == pytest.approx(100)
    assert results.loc[2, "initial_stock_val"] == pytest.approx(100)

    assert results.loc[0, "initial_constant_val"] == pytest.approx(50)
    assert results.loc[1, "initial_constant_val"] == pytest.approx(50)
    assert results.loc[2, "initial_constant_val"] == pytest.approx(50)


def test_model_plot_method(tmp_path):
    # This test requires matplotlib and will generate a file.
    # tmp_path is a pytest fixture for a temporary directory.

    # 1. Run a simple model
    model = Model("plot_test", dt=1.0)
    population = Stock("population", 100)
    birth_rate = Constant("birth_rate", 0.1)
    births_eq = population * birth_rate
    births = Flow("births", equation=births_eq)
    population.add_inflow(births)
    model.add(population, birth_rate, births)
    results = model.run(duration=3)

    # 2. Call the plot method with save_path specified
    plot_file = tmp_path / "test_plot.png"
    model.plot(results, columns=["population"], save_path=plot_file)

    # 3. Assert that the file exists at the specified path
    assert plot_file.exists()
    assert plot_file.is_file()

    # 4. Clean up the created file (pytest's tmp_path handles directory cleanup)
    # No explicit cleanup needed for the file as tmp_path will clean up the directory.
