from mead.symbols import Stock, Flow, Auxiliary, Constant, Delay
from mead.model import Model
from mead.graph import Graph

# --- Parameters ---
tap_rate = Constant("Tap rate", 5.0)           # units of water per time
mop_base_rate = Constant("Mop base rate", 4.0) # base mopping speed
# Optionally, an auxiliary mop speed multiplier: faster mopping if more water

# --- Stock: Water on Floor ---
water = Stock("Water on Floor", initial_value=0.0)

mop_efficiency = Auxiliary(
    "Mop efficiency",
    formula=lambda: 1.0 / (1 + water.value)  # example: efficiency drops as water increases
)

# --- Inflow: Water from Faucet / Tap ---
tap_flow = Flow("Tap flow", formula=lambda: float(tap_rate))

# --- Outflow: Mopping ---
# Mopping rate depends on base rate and how full the floor is (optionally)
def mop_formula():
    # Could use water.value to scale mop speed, or keep it constant
    return float(mop_base_rate) * float(mop_efficiency)

mop_flow = Flow("Mop flow", formula=mop_formula)

# --- Wiring ---
water.add_inflow(tap_flow)
water.add_outflow(mop_flow)

# --- Build and Run Model ---
m = Model(steps=1000, stocks=[water], dt=0.001)

history = m.run()
history["mop_flow"] = mop_flow.history
Graph().plot(history)
