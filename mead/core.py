from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence
from collections.abc import Callable

# prevents circular import
if TYPE_CHECKING:
    from mead.model import Model


class Element:
    """The base class for all model elements."""

    def __init__(self, name: str):
        self.name = name
        self.model: Model | None = None

    def __add__(self, other: Any) -> Equation:
        return Equation(self, "+", other)

    def __radd__(self, other: Any) -> Equation:
        return Equation(other, "+", self)

    def __sub__(self, other: Any) -> Equation:
        return Equation(self, "-", other)

    def __rsub__(self, other: Any) -> Equation:
        return Equation(other, "-", self)

    def __mul__(self, other: Any) -> Equation:
        return Equation(self, "*", other)

    def __rmul__(self, other: Any) -> Equation:
        return Equation(other, "*", self)

    def __truediv__(self, other: Any) -> Equation:
        return Equation(self, "/", other)

    def __rtruediv__(self, other: Any) -> Equation:
        return Equation(other, "/", self)

    def __neg__(self) -> Equation:
        return Equation(0, "-", self)  # Negation as 0 - self

    # Comparisons...
    # Overriding __eq__ leads to hash errors, for numerical
    # comparison such as a == b, we can (a <= b) * (a >= b) == 1
    def __gt__(self, other) -> Equation:
        return Equation(self, ">", other)

    def __lt__(self, other) -> Equation:
        return Equation(self, "<", other)

    def __ge__(self, other) -> Equation:
        return Equation(self, ">=", other)

    def __le__(self, other) -> Equation:
        return Equation(self, "<=", other)

    def compute(self, context: dict[str, Any]) -> float:
        """Computes the value of the element based on the current model context."""
        # By default, an element's value is its current state in the model
        return context["state"].get(self.name, 0.0)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class Constant(Element):
    """An element with a fixed value."""

    def __init__(self, name: str, value: float):
        super().__init__(name)
        self.value = value

    def compute(self, context: dict[str, Any]) -> float:
        return self.value

    def __repr__(self) -> str:
        return f"{super().__repr__()}, value={self.value})"


class Function(Element):
    r""" A callable function with no dependencies
    """

    def __init__(self, name: str, func: Callable[[dict[str, Any]], float]):
        r"""
        Arguments
        ---------
        name : str
            A unique name in the model to refer to this element
        func : Callable[ctx, float]
            A function in the form of `function(ctx) -> float` that will
            be called during model processing.
        """
        super().__init__(name)
        self.value = func

    def compute(self, context: dict[str, Any]) -> float:
        return self.value(context)

    def __repr__(self) -> str:
        return f"{super().__repr__()}, value={self.value})"


class Auxiliary(Element):
    """An element representing a named equation, useful for intermediate calculations."""

    def __init__(self, name: str, equation: Element):
        super().__init__(name)
        self.equation = equation

    def compute(self, context: dict[str, Any]) -> float:
        return self.equation.compute(context)

    @property
    def dependencies(self) -> list[Element]:
        return [self.equation]  # Auxiliary directly depends on its equation

    def __repr__(self) -> str:
        return f"{super().__repr__()}, equation={self.equation!r})"


class Time(Element):
    """ Returns current time of simulation
    """
    def __init__(self, name: str):
        super().__init__(name)
    
    def compute(self, context: dict[str, Any]) -> float:
        return context.get("time", 0.0)

    def __repr__(self) -> str:
        return f"{super().__repr__()})"


import operator

# Map operator symbols to functions
_OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
}


class Equation(Element):
    """An element representing a mathematical operation between other elements."""

    def __init__(self, left: Any, op: str, right: Any):
        _left_element = (
            left
            if isinstance(left, Element)
            else Constant(f"literal_{left}", float(left))
        )
        _right_element = (
            right
            if isinstance(right, Element)
            else Constant(f"literal_{right}", float(right))
        )
        _name = f"({_left_element.name} {op} {_right_element.name})"  # Generate name correctly

        super().__init__(_name)
        self.left = _left_element
        self.right = _right_element
        self.op = op
        if self.op not in _OPERATORS:
            raise ValueError(f"Unknown operator: {self.op}")

    def compute(self, context: dict[str, Any]) -> float:
        left_val = self.left.compute(context)
        right_val = self.right.compute(context)

        # Handle safe division explicitly before using the operator
        if self.op == "/" and right_val == 0:
            return 0.0

        return _OPERATORS[self.op](left_val, right_val)

    @property
    def dependencies(self) -> list[Element]:
        deps = []
        if isinstance(self.left, Element) and not (
            isinstance(self.left, Constant) and self.left.name.startswith("literal_")
        ):
            deps.append(self.left)
        if isinstance(self.right, Element) and not (
            isinstance(self.right, Constant) and self.right.name.startswith("literal_")
        ):
            deps.append(self.right)
        return list(set(deps))  # Remove duplicates

    def __repr__(self) -> str:
        return f"{super().__repr__()}, op={self.op!r}, left={self.left.name!r}, right={self.right.name!r})"
