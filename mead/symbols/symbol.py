from collections.abc import Callable
from mead.symbols import Historical

import logging

logger = logging.getLogger(__name__)

class BaseSymbol(Historical):

    def __init__(self, name: str, formula: Callable[..., float] | None = None):
        super().__init__()
        self.name = name
        self.formula = formula
        self.result: float = 0.0

    def compute(self) -> float:
        if self.formula is not None:
            self.result = self.formula()
            logger.debug(f"{self!r}.compute()={self.result}")
        self.record(self.result)
        return float(self.result)

    def __float__(self):
        return self.compute()

    def __add__(self, other):
        return float(self) + other

    def __radd__(self, other):
        return other + float(self)

    def __sub__(self, other):
        return float(self) - other

    def __rsub__(self, other):
        return other - float(self)

    def __mul__(self, other):
        return float(self) * other

    def __rmul__(self, other):
        return other * float(self)

    def __truediv__(self, other):
        return float(self) / other

    def __rtruediv__(self, other):
        return other / float(self)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, result={self.result})"


class Flow(BaseSymbol):
    pass


class Auxiliary(BaseSymbol):
    pass


class Constant(BaseSymbol):

    def __init__(self, name: str, value: float):
        super().__init__(name, lambda: value)
        self.result = value
        self.record(value)
