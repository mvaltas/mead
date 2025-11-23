import pytest
from mead import Stock, Flow, Model
from mead.flow import fractional


def test_model_initialization():
    model = Model("test_model", dt=0.5)
    
    assert model.name == "test_model"
    assert model.dt == 0.5


def test_model_add_stock():
    model = Model("test")
    stock = Stock("x", 10)
    
    model.add_stock(stock)
    assert "x" in model._stocks


def test_model_duplicate_stock_error():
    model = Model("test")
    stock1 = Stock("x", 10)
    stock2 = Stock("x", 20)
    
    model.add_stock(stock1)
    
    with pytest.raises(ValueError, match="already exists"):
        model.add_stock(stock2)


def test_model_reset():
    model = Model("test")
    stock = Stock("x", 100)
    model.add_stock(stock)
    
    stock.set_value(500)
    assert stock.value == 500
    
    model.reset()
    assert stock.value == 100


def test_exponential_growth_euler():
    model = Model("growth", dt=0.25)
    
    population = Stock("population", 100)
    births = Flow("births", fractional("population", 0.1))
    population.add_inflow(births)
    
    model.add_stock(population)
    
    results = model.run(duration=10, method="euler")

    assert "time" in results.columns
    assert "population" in results.columns
    assert len(results) == 41

    assert results["population"].iloc[0] == 100
    assert results["population"].iloc[-1] > 100


def test_exponential_growth_rk4():
    model = Model("growth", dt=0.25)
    
    population = Stock("population", 100)
    births = Flow("births", fractional("population", 0.1))
    population.add_inflow(births)
    
    model.add_stock(population)
    
    results = model.run(duration=10, method="rk4")

    assert "time" in results.columns
    assert "population" in results.columns

    assert results["population"].iloc[0] == 100
    assert results["population"].iloc[-1] > 100


def test_goal_seeking():
    model = Model("goal", dt=0.25)
    
    target = 1000
    adjustment_time = 5
    
    inventory = Stock("inventory", 100)
    
    def adjustment_rate(ctx):
        gap = target - ctx["state"].get("inventory", 0)
        return gap / adjustment_time
    
    adjustment = Flow("adjustment", adjustment_rate)
    inventory.add_inflow(adjustment)
    
    model.add_stock(inventory)
    
    results = model.run(duration=30, method="euler")

    final_value = results["inventory"].iloc[-1]
    assert final_value > 900
    assert final_value < 1100


def test_invalid_integration_method():
    model = Model("test")
    stock = Stock("x", 10)
    model.add_stock(stock)
    
    with pytest.raises(ValueError, match="Unknown integration method"):
        model.run(duration=10, method="invalid")

