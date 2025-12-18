from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Tuple

from mead.core import Element
from mead.stock import Stock
from mead.utils import as_element

if TYPE_CHECKING:
    from mead.model import Model


class Delay(Element):
    """
    An element that returns a delayed value of an input.
    Requires the model to manage history.
    """

    def __init__(self, name: str, input: Element, delay_time: float | Element):
        super().__init__(name)
        self.input = input
        self.delay_time = as_element(delay_time)

    def compute(self, context: dict[str, Any]) -> float:
        history_lookup = context.get("history_lookup")
        if not history_lookup:
            raise RuntimeError(
                "Delay element requires a 'history_lookup' function in the context."
            )

        computed_delay_time = self.delay_time.compute(
            context
        )  # Compute the value of delay_time
        return history_lookup(self.input.name, computed_delay_time)

    @property
    def dependencies(self) -> list[Element]:
        return [self.input, self.delay_time]

    def __repr__(self) -> str:
        return f"Delay({self.name=!r}, {self.input.name=!r}, {self.delay_time=!r})"


class Smooth(Element):
    """
    An element that computes an exponential smooth of an input.
    smooth_value(t) = smooth_value(t-dt) + (dt / smoothing_time) * (input_value(t) - smooth_value(t-dt))
    Requires the model to manage history of this smooth element itself.
    """

    def __init__(
        self,
        name: str,
        target_value: float | Element,
        smoothing_time: float | Element,
        initial_value: float | Element = 0.0,
    ):
        super().__init__(name)
        self.target_value = as_element(target_value)
        self.smoothing_time = as_element(smoothing_time)
        self.initial_value = as_element(initial_value)

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context["time"]
        if current_time == 0.0:
            return self.initial_value.compute(context)

        history_lookup = context["history_lookup"]
        dt = context["dt"]

        input_val = self.target_value.compute(context)
        smoothing_time_val = self.smoothing_time.compute(context)

        # Get the previous value of THIS smooth element
        previous_smooth_val = history_lookup(self.name, dt)

        if smoothing_time_val == 0:  # Avoid division by zero
            return input_val

        # Exponential smoothing formula
        return previous_smooth_val + (dt / smoothing_time_val) * (
            input_val - previous_smooth_val
        )

    @property
    def dependencies(self) -> list[Element]:
        return [self.target_value, self.smoothing_time, self.initial_value]

    def __repr__(self) -> str:
        return f"Smooth({self.name=!r}, {self.target_value.name=!r}, {self.smoothing_time.name=!r}, {self.initial_value=!r})"


class Table(Element):
    """
    An element that performs a lookup from a table (functional relationship)
    using linear interpolation.
    """

    def __init__(
        self, name: str, input: float | Element, points: Sequence[Tuple[float, float]]
    ):
        super().__init__(name)
        self.input_element = as_element(input)
        # Ensure points are sorted by x-value
        self.points = sorted(points, key=lambda p: p[0])

        if len(self.points) < 2:
            raise ValueError("Table must have at least two points for interpolation.")

    def compute(self, context: dict[str, Any]) -> float:
        input_val = self.input_element.compute(context)

        # extrapolation (return first/last y-value)
        if input_val <= self.points[0][0]:
            return self.points[0][1]
        if input_val >= self.points[-1][0]:
            return self.points[-1][1]

        # Find the interval for interpolation
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]

            if x1 <= input_val <= x2:
                # Linear interpolation
                if x1 == x2:  # Avoid division by zero
                    return (y1 + y2) / 2

                return y1 + (input_val - x1) * (y2 - y1) / (x2 - x1)

        return 0.0  # Fallback

    @property
    def dependencies(self) -> list[Element]:
        return [self.input_element]

    def __repr__(self) -> str:
        return f"Table({self.name=!r}, {self.input_element.name=!r}, {self.points=!r})"


class IfThenElse(Element):
    """
    An element that represents conditional logic.
    If condition > 0, returns the true_element's value, else returns the false_element's value.
    """

    def __init__(
        self,
        name: str,
        condition: float | Element,
        true_element: float | Element,
        false_element: float | Element,
    ):
        super().__init__(name)
        self.condition = as_element(condition)
        self.true_element = as_element(true_element)
        self.false_element = as_element(false_element)

    def compute(self, context: dict[str, Any]) -> float:
        condition_val = self.condition.compute(context)
        if condition_val > 0:
            return self.true_element.compute(context)
        else:
            return self.false_element.compute(context)

    @property
    def dependencies(self) -> list[Element]:
        return [self.condition, self.true_element, self.false_element]

    def __repr__(self) -> str:
        return (
            f"IfThenElse({self.name=!r}, {self.condition.name=!r}, "
            f"{self.true_element.name=!r}, {self.false_element.name=!r})"
        )


class Min(Element):
    """
    An element that returns the minimum of its input elements.
    """

    def __init__(self, name: str, *input_elements: float | Element):
        super().__init__(name)
        if not input_elements:
            raise ValueError("Min element must have at least one input element.")
        self.input_elements = [as_element(i) for i in input_elements]

    def compute(self, context: dict[str, Any]) -> float:
        return min(el.compute(context) for el in self.input_elements)

    @property
    def dependencies(self) -> list[Element]:
        return self.input_elements

    def __repr__(self) -> str:
        return f"Min({self.name=!r}, {self.input_elements=!r})"


class Max(Element):
    """
    An element that returns the maximum of its input elements.
    """

    def __init__(self, name: str, *input_elements: float | Element):
        super().__init__(name)
        if not input_elements:
            raise ValueError("Max element must have at least one input element.")
        self.input_elements = [as_element(i) for i in input_elements]

    def compute(self, context: dict[str, Any]) -> float:
        return max(el.compute(context) for el in self.input_elements)

    @property
    def dependencies(self) -> list[Element]:
        return self.input_elements

    def __repr__(self) -> str:
        return f"Max({self.name=!r}, {self.input_elements=!r})"


class Pulse(Element):
    """
    An element that generates a pulse (a temporary burst) of a given magnitude.
    """

    def __init__(
        self,
        name: str,
        start_time: float | Element,
        duration: float | Element,
        ammount: float | Element,
    ):
        super().__init__(name)
        self.start_time = as_element(start_time)
        self.duration = as_element(duration)
        self.magnitude = as_element(ammount)

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context["time"]
        start = self.start_time.compute(context)
        dur = self.duration.compute(context)
        mag = self.magnitude.compute(context)

        if start <= current_time < start + dur:
            return mag
        return 0.0

    @property
    def dependencies(self) -> list[Element]:
        return [self.start_time, self.duration, self.magnitude]

    def __repr__(self) -> str:
        return (
            f"Pulse({self.name=!r}, {self.start_time.name=!r}, "
            f"{self.duration.name=!r}, {self.magnitude.name=!r})"
        )


class Step(Element):
    """
    An element that generates a step change in value at a specified start_time.
    """

    def __init__(
        self,
        name: str,
        start_time: float | Element,
        before_value: float | Element,
        after_value: float | Element,
    ):
        super().__init__(name)
        self.start_time = as_element(start_time)
        self.before_value = as_element(before_value)
        self.after_value = as_element(after_value)

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context["time"]
        start = self.start_time.compute(context)

        if current_time < start:
            return self.before_value.compute(context)
        else:
            return self.after_value.compute(context)

    @property
    def dependencies(self) -> list[Element]:
        return [self.start_time, self.before_value, self.after_value]

    def __repr__(self) -> str:
        return (
            f"Step({self.name=!r}, {self.start_time.name=!r}, "
            f"{self.before_value.name=!r}, {self.after_value.name=!r})"
        )


class Ramp(Element):
    """
    An element that generates a linearly increasing (or decreasing) value over a period.
    """

    def __init__(
        self,
        name: str,
        start_time: float | Element,
        end_time: float | Element,
        ammount: float | Element,
        initial_value: float | Element = 0.0,
    ):
        super().__init__(name)
        self.start_time = as_element(start_time)
        self.end_time = as_element(end_time)
        self.slope = as_element(ammount)
        self.initial_value = as_element(initial_value)

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context.get("time", 0.0)
        start = self.start_time.compute(context)
        end = self.end_time.compute(context)
        slp = self.slope.compute(context)
        initial = self.initial_value.compute(context)

        if current_time < start:
            return initial
        elif start <= current_time <= end:
            return initial + slp * (current_time - start)
        else:
            return initial + slp * (end - start)  # Hold the value at end_time

    @property
    def dependencies(self) -> list[Element]:
        return [self.start_time, self.end_time, self.slope, self.initial_value]

    def __repr__(self) -> str:
        return (
            f"Ramp({self.name=!r}, {self.start_time.name=!r}, "
            f"{self.end_time.name=!r}, {self.slope.name=!r}, "
            f"{self.initial_value.name=!r})"
        )


class Delay2(Element):
    """
    A second-order exponential delay element, implemented as a chain of two Smooth components.
    """

    def __init__(
        self,
        name: str,
        input_element: float | Element,
        delay_time: float | Element,
        initial_value: float | Element = 0.0,
    ):
        super().__init__(name)
        self.input_element = as_element(input_element)
        self.delay_time = as_element(delay_time)
        self.initial_value = as_element(initial_value)

        # The effective smoothing time for each stage of a second-order delay
        # is delay_time / 2.0
        smoothing_time_per_stage = as_element(self.delay_time / 2.0)

        # Chain two Smooth components
        self.smooth1 = Smooth(
            f"{name}_smooth1",
            self.input_element,
            smoothing_time_per_stage,
            self.initial_value,
        )
        self.smooth2 = Smooth(
            f"{name}_smooth2",
            self.smooth1,
            smoothing_time_per_stage,
            self.initial_value,
        )

    def compute(self, context: dict[str, Any]) -> float:
        # The output of Delay2 is the output of the final Smooth component
        return self.smooth2.compute(context)

    @property
    def dependencies(self) -> list[Element]:
        return [
            self.input_element,
            self.delay_time,
            self.initial_value,
            self.smooth1,
            self.smooth2,
        ]

    def __repr__(self) -> str:
        return (
            f"Delay2({self.name=!r}, {self.input_element.name=!r}, "
            f"{self.delay_time.name=!r}, {self.initial_value.name=!r})"
        )


class Delay3(Element):
    """
    A third-order exponential delay element, implemented as a chain of three Smooth components.
    """

    def __init__(
        self,
        name: str,
        input_element: float | Element,
        delay_time: float | Element,
        initial_value: float | Element = 0.0,
    ):
        super().__init__(name)
        self.input_element = as_element(input_element)
        self.delay_time = as_element(delay_time)
        self.initial_value = as_element(initial_value)

        # The effective smoothing time for each stage of a third-order delay
        # is delay_time / 3.0
        smoothing_time_per_stage = as_element(self.delay_time / 3.0)

        # Chain three Smooth components
        self.smooth1 = Smooth(
            f"{name}_smooth1",
            self.input_element,
            smoothing_time_per_stage,
            self.initial_value,
        )
        self.smooth2 = Smooth(
            f"{name}_smooth2",
            self.smooth1,
            smoothing_time_per_stage,
            self.initial_value,
        )
        self.smooth3 = Smooth(
            f"{name}_smooth3",
            self.smooth2,
            smoothing_time_per_stage,
            self.initial_value,
        )

    def compute(self, context: dict[str, Any]) -> float:
        # The output of Delay3 is the output of the final Smooth component
        return self.smooth3.compute(context)

    @property
    def dependencies(self) -> list[Element]:
        return [
            self.input_element,
            self.delay_time,
            self.initial_value,
            self.smooth1,
            self.smooth2,
            self.smooth3,
        ]

    def __repr__(self) -> str:
        return (
            f"Delay3({self.name=!r}, {self.input_element.name=!r}, "
            f"{self.delay_time.name=!r}, {self.initial_value.name=!r})"
        )


class Initial(Element):
    """
    An element that returns the initial value of an input element.
    """

    def __init__(self, name: str, input_element: Element):
        super().__init__(name)
        self.input_element = input_element

    def compute(self, context: dict[str, Any]) -> float:
        if isinstance(self.input_element, Stock):
            return self.input_element.initial_value

        # compute at t=0
        initial_context = {
            "time": 0.0,
            "state": (
                {el.name: el.initial_value for el in self.model.stocks.values()}
                if self.model
                else {}
            ),
            "history_lookup": lambda name, delay_time_param: 0.0,
            "dt": context.get("dt", 0.0),
        }
        return self.input_element.compute(initial_context)

    @property
    def dependencies(self) -> list[Element]:
        return [self.input_element]

    def __repr__(self) -> str:
        return f"Initial({self.name=!r}, {self.input_element.name=!r})"


class Policy(Element):
    """Models an intervention when condition is met"""

    def __init__(
        self, name: str, condition: Element, effect: float | Element, apply: int = 1
    ):
        """
        Args
        ----
            condition: A condition that if True will trigger the policy
            effect: Resulting effect
            apply(int): How many times the policy will by applied, -1 == always
        """
        super().__init__(name)
        self.condition = condition
        self.effect = as_element(effect)
        self.apply = apply
        self._apply_mem: dict[float, float] = {}

    def compute(self, context: dict[str, Any]) -> float:
        time = context["time"]
        # reuse results if already applied to this time
        if time in self._apply_mem:
            return self._apply_mem[time]

        cond = self.condition.compute(context)
        # if counter < 0, always apply policy
        if self.apply == 0:
            return 0.0
        elif cond == True:
            # appling policy, decrement application
            self.apply -= 1
            result = self.effect.compute(context) / context["dt"]
            # save results
            self._apply_mem[time] = result
            return result
        else:
            return 0.0

    @property
    def dependencies(self) -> list[Element]:
        return [self.condition, self.effect]

    def __repr__(self) -> str:
        return f"Policy({self.name=!r}, {self.condition=!r}, {self.effect=!r}, {self.apply=!r})"


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

    def __repr__(self) -> str:
        return f"Flow({self.name!r}, {self.equation=!r})"
