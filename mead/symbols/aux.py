from collections.abc import Callable

import logging

logger = logging.getLogger(__name__)

class Auxiliary:
    def __init__(self, name: str, formula: Callable[..., float]):
        self.name = name
        self.formula = formula

    def compute(self) -> float:
        result = self.formula()
        logger.debug(f"{self!r}, compute={result}")
        return result

    def __repr__(self) -> str:
        return f"Auxiliary(name={self.name!r}, formula={self.formula!r})"
