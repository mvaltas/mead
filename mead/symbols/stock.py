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

    def net_flow(self, step: int):
        total_in = sum(f.compute(step) for f in self.inflows)
        total_out = sum(f.compute(step) for f in self.outflows)
        d = total_in - total_out
        logger.debug(f"{self} total_inflows={total_in} total_outflows={total_out} delta={d}")
        return d

    def __setattr__(self, key, val):
        # clamp stock at zero
        if key == "value":
            val = max(0, val)
        super().__setattr__(key, val)

    def __repr__(self):
        return (
            f"Stock(name={self.name}, "
            f"initial_value={self.initial_value}, "
            f"value={self.value}, "
            f"inflows={self.inflows}, "
            f"outflows={self.outflows})"
        )

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"
