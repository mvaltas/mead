from mead.symbols import Stock, Flow


def test_stock_with_no_flow_is_constant():
    stock = Stock("test_stock", 10.0)
    stock.update(dt=1.0, step=0)
    stock.update(dt=1.0, step=1)
    assert stock.value == 10.0


def test_stock_updates_with_an_inflow():
    stock = Stock("population", 10.0)
    births = Flow("births", lambda: 1.0)
    stock.add_inflow(births)
    births.compute()
    stock.update(dt=1.0, step=0)
    assert stock.value == 11.0


def test_stock_updates_with_an_outflow():
    stock = Stock("population", 10.0)
    deaths = Flow("deaths", lambda: 1.0)
    stock.add_outflow(deaths)
    deaths.compute()
    stock.update(dt=1.0, step=0)
    assert stock.value == 9.0


def test_stock_updates_with_both_inflow_and_outflow():
    stock = Stock("population", 10.0)

    births = Flow("births", lambda: 1.0)
    stock.add_inflow(births)

    deaths = Flow("deaths", lambda: 1.0)
    stock.add_outflow(deaths)

    births.compute()
    deaths.compute()

    stock.update(dt=1.0, step=0)
    assert stock.value == 10.00


def test_stock_can_have_multiple_inflows():
    stock = Stock("population", 10.0)
    births = Flow("births", lambda: 1.0)
    immigration = Flow("immigration", lambda: 1.0)

    stock.add_inflow(births, immigration)

    births.compute()
    immigration.compute()

    stock.update(dt=1.0, step=0)
    assert stock.value == 12.0


def test_stock_can_have_multiple_outflows():
    stock = Stock("population", 10.0)
    deaths = Flow("deaths", lambda: 1.0)
    emmigration = Flow("emmigration", lambda: 1.0)

    stock.add_outflow(deaths, emmigration)

    deaths.compute()
    emmigration.compute()

    stock.update(dt=1.0, step=0)
    assert stock.value == 8.0
