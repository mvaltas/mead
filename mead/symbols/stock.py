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
        self.history: list[float] = []

    def add_inflow(self, *flows: Flow):
        for f in flows:
            self.inflows.append(f)

    def add_outflow(self, *flows: Flow):
        for f in flows:
            self.outflows.append(f)

    def update(self, dt: float):
        total_in = sum(f.result for f in self.inflows)
        total_out = sum(f.result for f in self.outflows)
        self.value += (total_in - total_out) * dt

        logger.info(f"Stock(name={self.name!r}, value={self.value!r}))")
        # stocks can't be negative
        if self.value < 0:
            logger.debug(f"{self} reached zero")
            self.value = 0
        self.history.append(self.value)
        return self.value

    def __repr__(self):
        return (
            f"Stock(name={self.name}, "
            f"initial_value={self.initial_value}, "
            f"value={self.value}, "
            f"inflows={self.inflows}, "
            f"outflows={self.outflows})"
        )
