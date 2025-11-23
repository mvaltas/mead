from mead import Flow, Model, Stock
from mead.flow import fractional, smoothed, single_pulse, constant, step, ramp, clip, sum_stocks, max_stocks, min_stocks, table_lookup, delayed

time_step = 1

model = Model("Functions Demo", dt=time_step)

all_stocks = []

def create_demo(name, function, initial: float=0):
    stock = Stock(name, initial_value=initial)
    flow = Flow(name, equation=function)
    stock.add_inflow(flow)
    model.add_stock(stock)
    all_stocks.append(name)


create_demo("step", step(2, 2))
create_demo("ramp", ramp(slope=0.5, start=1, end=8))

# Adds fraction of stock to stock, exp growth
create_demo("fractional", fractional("fractional", 0.2), initial=1)

# Send pulse from start for duration steps
create_demo("single_pulse", single_pulse(pulse=30, start=0, duration=2))

# Seek goal in tau steps
create_demo("smoothed", smoothed("smoothed", constant(10), tau=10), initial=40)


# Clip, bounce oscilates but clip caps changes to -10/10 instead of -100/100
def bounce(ctx):
    if ctx["time"] != 0 and ctx["state"]["clip"] % ctx["time"] == 0:
        return 100
    else:
        return -100

create_demo("clip", clip(value_func=bounce, min_val=-10, max_val=10), initial=30)

# Sum of stocks (divided by 50 otherwise overshoots)
create_demo("sum_stocks", lambda ctx: sum_stocks(*all_stocks)(ctx) / 50)
# Min of stocks
create_demo("min_stocks", min_stocks(*all_stocks))
# Max of stocks
create_demo("max_stocks", lambda ctx: max_stocks(*all_stocks)(ctx) / 50)

# Lookup table, if value < first_key => first_key, value > last_key => last_key
# interpolate values in between
table: dict[float, float] = {0: 1, 10: 1.5, 30: 2}
create_demo("table_lookup", table_lookup("table_lookup", table), initial=0)

source_stock = Stock("source", initial_value=1)
target_stock = Stock("delayed", initial_value=10)
delayed_flow = Flow("source_to_target", delayed("source", delay_time=3))
source_stock.add_outflow(delayed_flow)
target_stock.add_inflow(delayed_flow)

all_stocks.append("delayed")

model.add_stock(source_stock)
model.add_stock(target_stock)



results = model.run(duration=20)
print(results.head(20))

model.plot(results, *all_stocks)
