import logging

from mead.symbols import Flow

logger = logging.getLogger(__name__)


class Stock:
    def __init__(self, name: str, initial_value: float = 0.0):
        self.name = name
        self.initial_value = initial_value
        self.value = self.initial_value
        self.inflows: list[Flow] = []
        self.outflows: list[Flow] = []
        self.total_in: float = 0.0
        self.total_out: float = 0.0

    def add_inflow(self, *flows: Flow):
        for f in flows:
            self.inflows.append(f)

    def add_outflow(self, *flows: Flow):
        for f in flows:
            self.outflows.append(f)

    def update(self, dt: float):
        self.total_in = sum(f.result for f in self.inflows)
        self.total_out = sum(f.result for f in self.outflows)
        self.value += (self.total_in - self.total_out) * dt
        # stocks can't be negative
        if self.value < 0:
            logger.debug(f"{self} reached zero")
            self.value = 0
        return self.value

    def __repr__(self):
        return (
            f"Stock(name={self.name}, "
            f"initial_value={self.initial_value}, "
            f"value={self.value}, "
            f"inflows={self.inflows}, "
            f"outflows={self.outflows}, "
            f"total_in={self.total_in}, "
            f"total_out={self.total_out})"
        )
