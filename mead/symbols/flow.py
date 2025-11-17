from collections.abc import Callable

import logging

logger = logging.getLogger(__name__)


class Flow:
    def __init__(self, name: str, formula: Callable[..., float]):
        self.name = name
        self.formula = formula
        self.result = 0.0

    def compute(self) -> float:
        self.result = self.formula()
        logger.debug(f"{self!r}.compute()={self.result}")
        return self.result

    def __repr__(self):
        return f"Flow(name={self.name})"
