
from mead import Stock, Flow


def test_stock_initialization():
    stock = Stock("population", 100)
    
    assert stock.name == "population"
    assert stock.initial_value == 100
    assert stock.value == 100


def test_stock_reset():
    stock = Stock("inventory", 50)
    stock.set_value(200)
    
    assert stock.value == 200
    
    stock.reset()
    assert stock.value == 50


def test_stock_add_flows():
    stock = Stock("water", 1000)
    
    inflow = Flow("rain", lambda t, s: 10)
    outflow = Flow("evaporation", lambda t, s: 5)
    
    stock.add_inflow(inflow)
    stock.add_outflow(outflow)
    
    assert len(stock._inflows) == 1
    assert len(stock._outflows) == 1


def test_stock_net_flow():
    stock = Stock("tank", 100)
    
    inflow = Flow("input", lambda t, s: 20)
    outflow = Flow("output", lambda t, s: 8)
    
    stock.add_inflow(inflow)
    stock.add_outflow(outflow)
    
    net = stock.net_flow(0, {"tank": 100})
    assert net == 12


def test_stock_net_flow_with_state():
    stock = Stock("population", 100)

    births = Flow("births", lambda t, s: 0.1 * s.get("population", 0))
    stock.add_inflow(births)

    net = stock.net_flow(0, {"population": 100})
    assert net == 10

    net = stock.net_flow(0, {"population": 200})
    assert net == 20

