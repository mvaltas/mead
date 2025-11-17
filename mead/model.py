import logging

from mead.symbols import Stock

logger = logging.getLogger(__name__)


class Model:
    def __init__(self):
        self.stocks = {}
        self.flows = {}
        self.time = 0

    def add_stock(self, stock: Stock):
        self.stocks[stock.name] = stock
        for flow in stock.inflows:
            if flow.name not in self.flows:
                self.flows[flow.name] = flow
        for flow in stock.outflows:
            if flow.name not in self.flows:
                self.flows[flow.name] = flow

    def step(self, dt=1.0):
        for f in self.flows.values():
            logger.debug(f"{f}.compute() START")
            f.compute()
            logger.debug(f"{f}.compute()={f.result} END")

        for s in self.stocks.values():
            logger.debug(f"{s}.update({dt}) START")
            s.update(dt)
            logger.debug(f"{s}.update({dt}) END")

        self.time += dt

    def run(self, steps, dt=1.0):
        history = {name: [] for name in self.stocks}
        for _ in range(steps):
            self.step(dt)
            for name, stock in self.stocks.items():
                history[name].append(stock.value)
        return history
