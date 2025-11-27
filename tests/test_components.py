import mead as m

def test_step():
    with m.Model("test", dt=1.0) as model:
        m.Step("step", start_time=5, before_value=10, after_value=20)

    results = model.run(duration=10)
    assert results.loc[4.0, "step"] == 10
    assert results.loc[5.0, "step"] == 20
    assert results.loc[6.0, "step"] == 20


def test_pulse():
    with m.Model("test", dt=1.0) as model:
        m.Pulse("pulse", start_time=2, duration=3, ammount=100)

    results = model.run(duration=6)
    assert results.loc[1.0, "pulse"] == 0
    assert results.loc[2.0, "pulse"] == 100
    assert results.loc[4.0, "pulse"] == 100
    assert results.loc[5.0, "pulse"] == 0


def test_ramp():
    with m.Model("test", dt=1.0) as model:
        m.Ramp("ramp", start_time=1, end_time=6, ammount=10, initial_value=5)

    results = model.run(duration=7)
    assert results.loc[0.0, "ramp"] == 5
    assert results.loc[1.0, "ramp"] == 5
    assert results.loc[3.0, "ramp"] == 25  # 5 + 10 * (3 - 1)
    assert results.loc[6.0, "ramp"] == 55  # 5 + 10 * (6 - 1)
    assert results.loc[7.0, "ramp"] == 55


def test_ifthenelse():
    with m.Model("test", dt=1.0) as model:
        time = m.Time("time")
        m.IfThenElse("ite", time - 5, 100, 200)

    results = model.run(duration=10)
    assert results.loc[4.0, "ite"] == 200  # time=4, cond=-1 -> 200
    assert results.loc[5.0, "ite"] == 200  # time=5, cond=0 -> 200
    assert results.loc[6.0, "ite"] == 100  # time=6, cond=1 -> 100


def test_min():
    with m.Model("test", dt=1.0) as model:
        time = m.Time("time")
        c1 = m.Constant("c1", 5)
        m.Min("min", time, c1)

    results = model.run(duration=10)
    assert results.loc[4.0, "min"] == 4  # min(4, 5)
    assert results.loc[5.0, "min"] == 5  # min(5, 5)
    assert results.loc[6.0, "min"] == 5  # min(6, 5)


def test_max():
    with m.Model("test", dt=1.0) as model:
        time = m.Time("time")
        c1 = m.Constant("c1", 5)
        m.Max("max", time, c1)

    results = model.run(duration=10)
    assert results.loc[4.0, "max"] == 5  # max(4, 5)
    assert results.loc[5.0, "max"] == 5  # max(5, 5)
    assert results.loc[6.0, "max"] == 6  # max(6, 5)


def test_table():
    with m.Model("test", dt=1.0) as model:
        time = m.Time("time")
        points = [(0, 10), (5, 20), (10, 0)]
        t = m.Table("table", time, points)

    results = model.run(duration=10)
    assert results.loc[0.0, "table"] == 10
    assert results.loc[2.0, "table"] == 14  # interpolated
    assert results.loc[5.0, "table"] == 20
    assert results.loc[10.0, "table"] == 0
    # Test extrapolation
    assert t.compute({"time": -1}) == 10
    assert t.compute({"time": 11}) == 0


def test_smooth():
    with m.Model("test", dt=0.25) as model:
        target = m.Step("target", 1, 100, 200)
        m.Smooth("smooth", target, smoothing_time=2.0, initial_value=100)

    results = model.run(duration=5)
    assert results.loc[0.0, "smooth"] == 100  # Initial value
    # After step, it should start moving towards 200
    assert results.loc[1.0, "smooth"] > 100  # at time 1.0
    assert results.loc[1.25, "smooth"] > results.loc[1.0, "smooth"]
    # Check that it approaches 200
    assert results.loc[5, "smooth"] > 150
    assert results.loc[5, "smooth"] < 200


def test_delay():
    with m.Model("test", dt=0.25) as model:
        input_stock = m.Stock("input", initial_value=10)
        input_stock.add_inflow(
            m.Flow("flow", m.IfThenElse("inflow", m.Time("time") - 2, 40, 0))
        )  # Inflow starts at t=2
        m.Delay("delayed_input", input_stock, delay_time=2)

    results = model.run(duration=5)
    # The delayed value should be the initial value of the stock for the first 2s
    assert results.loc[0.0, "delayed_input"] == 10
    assert results.loc[2.0, "delayed_input"] == 10  # at time=2.0
    # After t=2, the stock starts increasing. This change should be seen
    # in the delayed output after t=4.
    assert results.loc[4.0, "delayed_input"] < results.loc[5.0, "delayed_input"]


def test_delay2():
    with m.Model("test", dt=0.25) as model:
        target = m.Step("target", 1, 100, 200)
        m.Delay2("delay2", target, delay_time=2.0, initial_value=100)

    results = model.run(duration=5)
    assert results.loc[0.0, "delay2"] == 100
    assert results.loc[1.0, "delay2"] > 100  # At time=1, starts increasing
    # Should be increasing towards 200, but slower than a Smooth
    assert results.loc[2.0, "delay2"] > 100


def test_delay3():
    with m.Model("test", dt=0.25) as model:
        target = m.Step("target", 1, 100, 200)
        m.Delay3("delay3", target, delay_time=3.0, initial_value=100)

    results = model.run(duration=5)
    assert results.loc[0.0, "delay3"] == 100
    assert results.loc[1.0, "delay3"] > 100  # At time=1, starts increasing
    # Should be increasing towards 200, but slower than Delay2
    assert results.loc[3.0, "delay3"] > 100


def test_initial():
    with m.Model("test", dt=1.0) as model:
        s = m.Stock("s", initial_value=50)
        s.add_inflow(m.Flow("flow",m.Constant("inflow", 10)))
        m.Initial("initial_s", s)

    results = model.run(duration=5)
    assert results.loc[0.0, "s"] == 50
    assert results.loc[1.0, "s"] == 60
    assert results.loc[0.0, "initial_s"] == 50
    assert results.loc[1.0, "initial_s"] == 50  # Should always be 50
    assert results.loc[5.0, "initial_s"] == 50
