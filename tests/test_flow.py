
from mead import Flow
from mead.flow import constant, fractional, table_lookup


def test_flow_initialization():
    flow = Flow("test_flow", lambda ctx: 5)
    
    assert flow.name == "test_flow"
    assert flow.rate({}) == 5


def test_flow_with_time():
    flow = Flow("time_dependent", lambda ctx: ctx["time"] * 2)
    
    assert flow.rate({"time": 0}) == 0
    assert flow.rate({"time": 5}) == 10
    assert flow.rate({"time": 10}) == 20


def test_flow_with_state():
    flow = Flow("state_dependent", lambda ctx: ctx["state"].get("x", 0) * 3)
    
    assert flow.rate({"state": {"x": 10}}) == 30
    assert flow.rate({"state": {"x": 20}}) == 60


def test_constant_helper():
    flow_func = constant(42)
    
    assert flow_func({}) == 42
    assert flow_func({"any": "state"}) == 42


def test_fractional_helper():
    flow_func = fractional("population", 0.1)
    
    assert flow_func({"state": {"population": 100}}) == 10
    assert flow_func({"state": {"population": 200}}) == 20
    assert flow_func({"state":{}}) == 0


def test_table_lookup_helper():
    table: dict[float, float] = {0: 0, 10: 100, 20: 150}
    flow_func = table_lookup("input", table)

    # precise table entry
    assert flow_func({"state": {"input": 0}}) == 0
    assert flow_func({"state": {"input": 10}}) == 100
    assert flow_func({"state": {"input": 20}}) == 150

    # interpolation in between values
    assert flow_func({"state": {"input": 5}}) == 50
    assert flow_func({"state": {"input": 15}}) == 125

    # value is bound by the table max/min
    assert flow_func({"state": {"input": -5}}) == 0
    assert flow_func({"state": {"input": 25}}) == 150
