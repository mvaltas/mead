import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


class Flow:
    def __init__(self, name: str, formula: Callable[..., float]):
        self.name = name
        self.formula = formula

    def compute(self):
        return self.formula()
