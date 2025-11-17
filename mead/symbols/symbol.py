from collections.abc import Callable
from collections import deque
from mead.symbols import Historical

import logging

logger = logging.getLogger(__name__)


class BaseSymbol(Historical):

    def __init__(self, name: str, formula: Callable[..., float] | None = None):
        super().__init__()
        self.name = name
        self.formula = formula
        self.result: float = 0.0
        self._last_step: int | None = None

    def compute(self, step: int | None = None) -> float:
        if step is not None and step == self._last_step:
            return self.result

        self.result = self.formula() if self.formula else self.result
        self._last_step = step
        logger.debug(f"{self!r}.compute(step={step!r})")
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


class Delay(BaseSymbol):

    def __init__(self, name: str, steps: int, input: BaseSymbol):
        super().__init__(name, formula=None)
        self.steps = steps
        self.buffer = deque([0.0] * steps, maxlen=steps)
        self.input_symbol = input

    def compute(self, step: int | None = None) -> float:
        if step is not None and step == self._last_step:
            return self.result

        self.result = self.buffer[0]

        input_value = self.input_symbol.compute(step)
        self.buffer.append(input_value)

        self._last_step = step
        logger.debug(f"{self!r}.compute(step={step!r})")
        self.record(self.result)

        return float(self.result)


class SmoothedAuxiliary(BaseSymbol):
    def __init__(self, name, input_symbol, tau_steps=10):
        super().__init__(name)
        self.input_symbol = input_symbol
        self.tau = tau_steps
        self.result = 0.0

    def compute(self, step: int | None =None):
        if step is not None and step == self._last_step:
            return self.result

        # target value from input symbol
        target = float(self.input_symbol.compute(step))
        # first-order lag toward target
        self.result += (target - self.result) / self.tau

        self._last_step = step
        logger.debug(f"{self!r}.compute(step={step!r})")
        self.record(self.result)

        return float(self.result)
