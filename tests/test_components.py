import pytest
from mead import (
    Model,
    Stock,
    Constant,
    Time,
    Delay,
    Smooth,
    Table,
    IfThenElse,
    Min,
    Max,
    Pulse,
    Step,
    Ramp,
    Delay2,
    Delay3,
    Initial,
)


def test_step():
    with Model("test", dt=1.0) as model:
        s = Step("step", start_time=5, before_value=10, after_value=20)

    results = model.run(duration=10)
    assert results.loc[4.0, "step"] == 10
    assert results.loc[5.0, "step"] == 20
    assert results.loc[6.0, "step"] == 20


def test_pulse():
    with Model("test", dt=1.0) as model:
        p = Pulse("pulse", start_time=2, duration=3, ammount=100)

    results = model.run(duration=6)
    assert results.loc[1.0, "pulse"] == 0
    assert results.loc[2.0, "pulse"] == 100
    assert results.loc[4.0, "pulse"] == 100
    assert results.loc[5.0, "pulse"] == 0


def test_ramp():
    with Model("test", dt=1.0) as model:
        r = Ramp("ramp", start_time=1, end_time=6, ammount=10, initial_value=5)

    results = model.run(duration=7)
    assert results.loc[0.0, "ramp"] == 5
    assert results.loc[1.0, "ramp"] == 5
    assert results.loc[3.0, "ramp"] == 25  # 5 + 10 * (3 - 1)
    assert results.loc[6.0, "ramp"] == 55  # 5 + 10 * (6 - 1)
    assert results.loc[7.0, "ramp"] == 55


def test_ifthenelse():
    with Model("test", dt=1.0) as model:
        time = Time("time")
        ite = IfThenElse("ite", time - 5, 100, 200)

    results = model.run(duration=10)
    assert results.loc[4.0, "ite"] == 200  # time=4, cond=-1 -> 200
    assert results.loc[5.0, "ite"] == 200  # time=5, cond=0 -> 200
    assert results.loc[6.0, "ite"] == 100  # time=6, cond=1 -> 100


def test_min():
    with Model("test", dt=1.0) as model:
        time = Time("time")
        c1 = Constant("c1", 5)
        m = Min("min", time, c1)

    results = model.run(duration=10)
    assert results.loc[4.0, "min"] == 4  # min(4, 5)
    assert results.loc[5.0, "min"] == 5  # min(5, 5)
    assert results.loc[6.0, "min"] == 5  # min(6, 5)


def test_max():
    with Model("test", dt=1.0) as model:
        time = Time("time")
        c1 = Constant("c1", 5)
        m = Max("max", time, c1)

    results = model.run(duration=10)
    assert results.loc[4.0, "max"] == 5  # max(4, 5)
    assert results.loc[5.0, "max"] == 5  # max(5, 5)
    assert results.loc[6.0, "max"] == 6  # max(6, 5)


def test_table():
    with Model("test", dt=1.0) as model:
        time = Time("time")
        points = [(0, 10), (5, 20), (10, 0)]
        t = Table("table", time, points)

    results = model.run(duration=10)
    assert results.loc[0.0, "table"] == 10
    assert results.loc[2.0, "table"] == 14  # interpolated
    assert results.loc[5.0, "table"] == 20
    assert results.loc[10.0, "table"] == 0
    # Test extrapolation
    assert t.compute({"time": -1}) == 10
    assert t.compute({"time": 11}) == 0


def test_smooth():
    with Model("test", dt=0.25) as model:
        target = Step("target", 1, 100, 200)
        s = Smooth("smooth", target, smoothing_time=2.0, initial_value=100)

    results = model.run(duration=5)
    assert results.loc[0.0, "smooth"] == 100  # Initial value
    # After step, it should start moving towards 200
    assert results.loc[1.0, "smooth"] > 100  # at time 1.0
    assert results.loc[1.25, "smooth"] > results.loc[1.0, "smooth"]
    # Check that it approaches 200
    assert results["smooth"].iloc[-1] > 150
    assert results["smooth"].iloc[-1] < 200


def test_delay():
    with Model("test", dt=0.25) as model:
        # Input is a stock that changes value
        input_stock = Stock("input", initial_value=10)
        input_stock.add_inflow(
            IfThenElse("inflow", Time("time") - 2, 40, 0)
        )  # Inflow starts at t=2
        # Delay the stock value by 2 time units
        d = Delay("delayed_input", input_stock, delay_time=2)

    results = model.run(duration=5)
    # The delayed value should be the initial value of the stock for the first 2s
    assert results.loc[0.0, "delayed_input"] == 10
    assert results.loc[2.0, "delayed_input"] == 10  # at time=2.0
    # After t=2, the stock starts increasing. This change should be seen
    # in the delayed output after t=4.
    assert results.loc[4.0, "delayed_input"] < results.loc[5.0, "delayed_input"]


def test_delay2():
    with Model("test", dt=0.25) as model:
        target = Step("target", 1, 100, 200)
        d2 = Delay2("delay2", target, delay_time=2.0, initial_value=100)

    results = model.run(duration=5)
    assert results.loc[0.0, "delay2"] == 100
    assert results.loc[1.0, "delay2"] > 100  # At time=1, starts increasing
    # Should be increasing towards 200, but slower than a Smooth
    assert results.loc[2.0, "delay2"] > 100


def test_delay3():
    with Model("test", dt=0.25) as model:
        target = Step("target", 1, 100, 200)
        d3 = Delay3("delay3", target, delay_time=3.0, initial_value=100)

    results = model.run(duration=5)
    assert results.loc[0.0, "delay3"] == 100
    assert results.loc[1.0, "delay3"] > 100  # At time=1, starts increasing
    # Should be increasing towards 200, but slower than Delay2
    assert results.loc[3.0, "delay3"] > 100


def test_initial():
    with Model("test", dt=1.0) as model:
        s = Stock("s", initial_value=50)
        s.add_inflow(Constant("inflow", 10))
        init = Initial("initial_s", s)

    results = model.run(duration=5)
    assert results.loc[0.0, "s"] == 50
    assert results.loc[1.0, "s"] == 60
    assert results.loc[0.0, "initial_s"] == 50
    assert results.loc[1.0, "initial_s"] == 50  # Should always be 50
    assert results.loc[5.0, "initial_s"] == 50
