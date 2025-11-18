import logging
from mead.symbols import Stock


logger = logging.getLogger(__name__)


class EulerSolver:
    def __init__(self, dt: float):
        self.dt = dt

    def step(self, stock: Stock, step: int):
        delta = stock.net_flow(step)
        stock.value += delta * self.dt
        logger.debug(f"stock.value += delta={delta} * dt={self.dt}")
        stock.record(stock.value)

    def __repr__(self):
        return f"{__class__.__name__}(dt={self.dt})"
