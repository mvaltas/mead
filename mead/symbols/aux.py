from collections.abc import Callable

import logging

logger = logging.getLogger(__name__)

class Auxiliary:
    def __init__(self, name: str, formula: Callable[..., float]):
        self.name = name
        self.formula = formula

    def compute(self) -> float:
        result = self.formula()
        logger.debug(f"Auxiliary(name={self.name}), compute={result}")
        return result
