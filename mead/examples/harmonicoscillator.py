import mead.symbols as ms
from mead.model import Model
from mead.graph import Graph

# Signed stock
class SignedStock(ms.Stock):
    def update(self, dt: float, step):
        total_in = sum(f.compute(step) for f in self.inflows)
        total_out = sum(f.compute(step) for f in self.outflows)
        self.value += (total_in - total_out) * dt
        self.result = self.value
        self.record(self.value)
        return self.value


m = ms.Constant("m", 1.0)  # mass
k = ms.Constant("k", 1.0)  # spring constant
c = ms.Constant("c", 0.0)  # damping


x = SignedStock("x", initial_value=1.0)   # position
v = SignedStock("v", initial_value=0.0)   # velocity

# dx/dt = v
dx = ms.Flow("dx", formula=lambda: v.value)

# dv/dt = -(k/m)x - (c/m)v
dv = ms.Flow(
    "dv",
    formula=lambda: -(float(k)/float(m))*x.value - (float(c)/float(m))*v.value
)

# connect flows
x.add_inflow(dx)
v.add_inflow(dv)


mdl = Model()
mdl.add_stock(x)
mdl.add_stock(v)

history = mdl.run(steps=1000, dt=0.01)

Graph().plot(history)
