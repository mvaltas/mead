from mead.core import Constant, Equation, Auxiliary, Delay
from mead.stock import Stock
from mead.flow import Flow
from mead.model import Model
import pytest

# Dummy context for testing elements in isolation within tests
dummy_context_model = {
    'state': {'population': 100, 'input_stock': 10, 'other': 50},
    'time': 0.0,
    'history_lookup': lambda name, delay_time: 123.0 # A simple, constant return for testing
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
    delayed_val = Delay("delayed_val", input_stock, 3.0) # Delay by 3 time units
    
    # Output stock receives the delayed value
    output_stock = Stock("output_stock", 0)
    output_flow = Flow("output_flow", delayed_val)
    output_stock.add_inflow(output_flow)
    
    model.add(input_stock, constant_rate, input_flow, delayed_val, output_stock, output_flow)
    
    results = model.run(duration=5)

    # input_stock will be 50, 60, 70, 80, 90, 100 at the start of each step
    assert results.loc[0, 'input_stock'] == 50
    assert results.loc[1, 'input_stock'] == 60
    assert results.loc[2, 'input_stock'] == 70
    assert results.loc[3, 'input_stock'] == 80
    assert results.loc[4, 'input_stock'] == 90
    assert results.loc[5, 'input_stock'] == 100

    # output_stock accumulates the delayed input_stock values
    # delayed_val is 0 for t=0,1,2 (delay time = 3)
    # At t=3, delayed_val gets value from input_stock at t=0 (50) -> inflow = 50. output_stock for t=3 is 0.
    # At t=4, delayed_val gets value from input_stock at t=1 (60) -> inflow = 60. output_stock for t=4 is 50.
    # At t=5, delayed_val gets value from input_stock at t=2 (70) -> inflow = 70. output_stock for t=5 is 50+60=110.

    assert results.loc[0, 'output_stock'] == 0
    assert results.loc[1, 'output_stock'] == 0
    assert results.loc[2, 'output_stock'] == 0
    assert results.loc[3, 'output_stock'] == 0 # At start of t=3, output_stock is still 0
    assert results.loc[4, 'output_stock'] == pytest.approx(50) # At start of t=4, output_stock has accumulated 50 from t=3
    assert results.loc[5, 'output_stock'] == pytest.approx(50 + 60) # At start of t=5, output_stock has accumulated 50+60 from t=3, t=4
