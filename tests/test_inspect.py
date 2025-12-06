import mead as m


def test_inspected_is_instance():
    inspected_stock = m.Inspect(m.Stock("stock", initial_value=10))
    assert isinstance(inspected_stock, m.Stock) == True


def test_print_was_called(capsys, ctx):
    inspected_stock = m.Inspect(m.Stock("stock", initial_value=10))
    inspected_stock.compute(ctx)
    out, _ = capsys.readouterr()
    assert "Inspect of Stock" in out


def test_hide_all_ommits_output(capsys, ctx):
    m.Inspect.config.__init__()  # reset config
    m.Inspect.config.hide_all = True
    inspected_stock = m.Inspect(m.Stock("stock", initial_value=10))
    inspected_stock.compute(ctx)
    out, _ = capsys.readouterr()
    assert out == ""


def test_hide_some_during_call(capsys, ctx):
    m.Inspect.config.__init__()  # reset config
    m.Inspect.config.hide("initial_value")
    inspected_stock = m.Inspect(m.Stock("stock", initial_value=10))
    inspected_stock.compute(ctx)
    out, _ = capsys.readouterr()
    assert "initial_value" not in out


def test_show_some_during_call(capsys, ctx):
    m.Inspect.config.__init__()  # reset config
    m.Inspect.config.hide_all = True
    m.Inspect.config.show("compute", "initial_value")
    inspected_stock = m.Inspect(m.Stock("stock", initial_value=10))
    inspected_stock.compute(ctx)
    out, _ = capsys.readouterr()
    assert "initial_value" in out
    assert "inflows" not in out
    assert "outflows" not in out


def test_show_some_during_print():
    m.Inspect.config.__init__()  # reset config
    m.Inspect.config.hide_all = True
    m.Inspect.config.show("initial_value")
    inspected_stock = m.Inspect(m.Stock("stock", initial_value=10))
    output = inspected_stock.__repr__()
    assert "initial_value" in output
    assert "inflows" not in output
    assert "outflows" not in output
