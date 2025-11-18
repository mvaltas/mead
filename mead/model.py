import logging

from mead.symbols import Stock

logger = logging.getLogger(__name__)


class Model:
    def __init__(self):
        self.stocks = {}
        self.flows = {}
        self.time = 0
        self.step = 0

    def add_stock(self, stock: Stock):
        self.stocks[stock.name] = stock
        for flow in stock.inflows:
            if flow.name not in self.flows:
                self.flows[flow.name] = flow
        for flow in stock.outflows:
            if flow.name not in self.flows:
                self.flows[flow.name] = flow

    def _step(self, dt: float, step: int):
        self.step = step
        for f in self.flows.values():
            f.compute(step)
            logger.debug(f"{f}.compute({step})={f.result}")

        for s in self.stocks.values():
            s.update(dt, step)
            logger.debug(f"{s}.update({dt}, {step})")

        self.time += dt

    def run(self, steps, dt=1.0):
        history = {name: [] for name in self.stocks}
        for s in range(steps):
            logger.info(f"RUN: step={s}, dt={dt}")
            self._step(dt, s)
            for name, stock in self.stocks.items():
                history[name].append(stock.value)
        return history
