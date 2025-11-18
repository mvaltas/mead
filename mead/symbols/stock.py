import logging

from mead.symbols import BaseSymbol
from mead.symbols import Historical

logger = logging.getLogger(__name__)


class Stock(Historical):
    def __init__(self, name: str, initial_value: float = 0.0):
        super().__init__()
        self.name = name
        self.initial_value = initial_value
        self.value = self.initial_value
        self.inflows: list[BaseSymbol] = []
        self.outflows: list[BaseSymbol] = []
        self.record(self.value)

    def add_inflow(self, *flows: BaseSymbol):
        self.inflows.extend(flows)

    def add_outflow(self, *flows: BaseSymbol):
        self.outflows.extend(flows)

    def update(self, dt: float, step: int):
        total_in = sum(f.compute(step) for f in self.inflows)
        total_out = sum(f.compute(step) for f in self.outflows)
        self.value += (total_in - total_out) * dt

        logger.info(f"Stock(name={self.name!r}, value={self.value!r}))")
        # stocks can't be negative
        if self.value < 0:
            logger.debug(f"{self} reached zero")
            self.value = 0
        self.record(self.value)
        return self.value

    def __repr__(self):
        return (
            f"Stock(name={self.name}, "
            f"initial_value={self.initial_value}, "
            f"value={self.value}, "
            f"inflows={self.inflows}, "
            f"outflows={self.outflows})"
        )
