import mead as m

time_step = 1

model = m.Model("Functions Demo", dt=time_step)

all_stocks = []

def create_demo(name, function, initial: float=0):
    stock = m.Stock(name, initial_value=initial)
    flow = m.Flow(name, equation=function)
    stock.add_inflow(flow)
    model.add_stock(stock)
    all_stocks.append(name)


create_demo("step", m.step(2, 2))
create_demo("ramp", m.ramp(slope=0.5, start=1, end=8))

# Adds fraction of stock to stock, exp growth
create_demo("fractional", m.fractional("fractional", 0.2), initial=1)

# Send pulse from start for duration steps
create_demo("single_pulse", m.single_pulse(pulse=30, start=0, duration=2))

# Seek goal in tau steps
create_demo("smoothed", m.smoothed("smoothed", m.constant(10), tau=10), initial=40)


# Clip, bounce oscilates but clip caps changes to -10/10 instead of -100/100
def bounce(t, s):
    if t != 0 and s["clip"] % t == 0:
        return 100
    else:
        return -100

create_demo("clip", m.clip(value_func=bounce, min_val=-10, max_val=10), initial=30)

# Sum of stocks (divided by 50 otherwise overshoots)
create_demo("sum_stocks", lambda t,s: m.sum_stocks(*all_stocks)(t,s) / 50)
# Min of stocks
create_demo("min_stocks", m.min_stocks(*all_stocks))
# Max of stocks
create_demo("max_stocks", lambda t, s: m.max_stocks(*all_stocks)(t,s) / 50)

# Lookup table, if value < first_key => first_key, value > last_key => last_key
# interpolate values in between
table: dict[float, float] = {0: 1, 10: 1.5, 30: 2}
create_demo("table_lookup", m.table_lookup("table_lookup", table), initial=0)


results = model.run(duration=20)
print(results.head(20))

model.plot(results, *all_stocks)
