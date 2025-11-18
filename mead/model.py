import logging

from mead.solvers import EulerSolver
from mead.symbols import Stock

logger = logging.getLogger(__name__)


class Model:
    def __init__(
        self,
        steps: int,
        dt: float = 1.0,
        solver_cls=EulerSolver,
        stocks: list[Stock] = [],
    ):
        self.stocks = {}
        self.flows = {}
        self.steps = steps
        self.dt = dt
        self.solver = solver_cls(dt)
        self._time_keeper = 0
        self._step_counter = 0

        if stocks:
            self.add_stock(stocks)

    def add_stock(self, stocks: list[Stock] | Stock):
        if isinstance(stocks, list):
            for s in stocks:
                self._load_stock(s)
        else:
            self._load_stock(stocks)

    def _load_stock(self, stock: Stock):
        self.stocks[stock.name] = stock
        for flow in stock.inflows:
            if flow.name not in self.flows:
                self.flows[flow.name] = flow
        for flow in stock.outflows:
            if flow.name not in self.flows:
                self.flows[flow.name] = flow

    def _step(self, step: int):
        self._step_counter = step
        for f in self.flows.values():
            f.compute(step)
            logger.debug(f"{f}.compute({step})={f.result}")

        for s in self.stocks.values():
            self.solver.step(s, step)
            logger.debug(f"{self.solver}.step({s}, {step})")

        self._time_keeper += self.dt

    def run(self):
        history = {name: [] for name in self.stocks}
        for s in range(self.steps):
            logger.info(
                f"RUN: step={s}, dt={self.dt}, time={self._time_keeper}, steps_taken=({self._step_counter}/{self.steps})"
            )
            self._step(s)
            for name, stock in self.stocks.items():
                history[name].append(stock.value)
        return history
