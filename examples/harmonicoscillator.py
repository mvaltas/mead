import mead.symbols as ms
from mead.old_model import Model
from mead.graph import Graph


# Signed stock (not recommended)
class SignedStock(ms.Stock):
    def __setattr__(self, key, val):
        # bypass zero clamp in default stock
        object.__setattr__(self, key, val)


m = ms.Constant("m", 1.0)  # mass
k = ms.Constant("k", 1.0)  # spring constant
c = ms.Constant("c", 0.0)  # damping


x = SignedStock("x", initial_value=1.0)  # position
v = SignedStock("v", initial_value=0.0)  # velocity

# dx/dt = v
dx = ms.Flow("dx", formula=lambda: v.value)

# dv/dt = -(k/m)x - (c/m)v
dv = ms.Flow(
    "dv",
    formula=lambda: -(float(k) / float(m)) * x.value - (float(c) / float(m)) * v.value,
)

# connect flows
x.add_inflow(dx)
v.add_inflow(dv)

mdl = Model(steps=1000, dt=0.01, stocks=[x, v])

Graph().plot(mdl.run())
