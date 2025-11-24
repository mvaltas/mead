from typing import Any
from mead.core import Element, Equation
from mead.stock import Stock  # Import Stock from its own module
from mead.utils import as_element


class Flow(Element):
    """
    A Flow represents a rate of change in the model.
    Its value is determined by its equation.
    """

    def __init__(self, name: str, equation: float | Element):
        super().__init__(name)
        self.equation = as_element(equation)

    def compute(self, context: dict[str, Any]) -> float:
        """Computes the flow's rate by evaluating its equation."""
        return self.equation.compute(context)

    @property
    def dependencies(self) -> list[Element]:
        """Returns the dependencies of the flow's equation."""
        deps = [self.equation]
        if hasattr(self.equation, "dependencies"):
            deps.extend(self.equation.dependencies)
        return deps


def goal_flow(
    name: str, stock: Stock, target: Element, adjustment_time: Element
) -> Flow:
    """
    Creates a Flow that adjusts a stock towards a target over an adjustment time.
    """
    gap = target - stock
    rate_equation = gap / adjustment_time
    return Flow(name, equation=rate_equation)
