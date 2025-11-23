from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Tuple # Added Sequence and Tuple

from mead.core import Element, Constant, Equation # Equation needed for Smooth's internal logic
if TYPE_CHECKING:
    from mead.model import Model
    from mead.stock import Stock


def _to_element(value: Any) -> Element:
    match value:
        case float()|int():
            return Constant(f"literal_{value}", value)
        case Element():
            return value
        case _:
            raise ValueError(f"Can't handle type of {value}")


# Delay component moved from core.py
class Delay(Element):
    """
    An element that returns a delayed value of an input Stock.
    Requires the model to manage history.
    """
    def __init__(self, name: str, input_stock: Stock, delay_time: Element): # delay_time can be an Element
        super().__init__(name)
        self.input_stock = input_stock
        self.delay_time = delay_time

    def compute(self, context: dict[str, Any]) -> float:
        history_lookup = context.get('history_lookup')
        if not history_lookup:
            raise RuntimeError("Delay element requires a 'history_lookup' function in the context.")
        
        computed_delay_time = self.delay_time.compute(context) # Compute the value of delay_time
        return history_lookup(self.input_stock.name, computed_delay_time)

    @property
    def dependencies(self) -> list[Element]:
        return [self.input_stock]

    def __repr__(self) -> str:
        return f"{super().__repr__()}, input_stock={self.input_stock.name!r}, delay_time={self.delay_time})"

class Smooth(Element):
    """
    An element that computes an exponential smooth of an input.
    smooth_value(t) = smooth_value(t-dt) + (dt / smoothing_time) * (input_value(t) - smooth_value(t-dt))
    Requires the model to manage history of this smooth element itself.
    """
    def __init__(self, name: str, input_element: Element, smoothing_time: Element, initial_value: float = 0.0):
        super().__init__(name)
        self.input_element = input_element
        self.smoothing_time = smoothing_time
        self.initial_value = initial_value

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context.get('time')
        if current_time == 0.0:
            return self.initial_value
            
        history_lookup = context.get('history_lookup')
        dt = context.get('dt')

        if not history_lookup or dt is None:
            raise RuntimeError("Smooth element requires 'history_lookup' and 'dt' in the context.")

        input_val = self.input_element.compute(context)
        smoothing_time_val = self.smoothing_time.compute(context)

        # Get the previous value of THIS smooth element
        previous_smooth_val = history_lookup(self.name, dt)
        
        if smoothing_time_val == 0: # Avoid division by zero
            return input_val
        
        # Exponential smoothing formula
        return previous_smooth_val + (dt / smoothing_time_val) * (input_val - previous_smooth_val)

    @property
    def dependencies(self) -> list[Element]:
        deps = [self.input_element, self.smoothing_time]
        if hasattr(self.input_element, 'dependencies'):
            deps.extend(self.input_element.dependencies)
        if hasattr(self.smoothing_time, 'dependencies'):
            deps.extend(self.smoothing_time.dependencies)
        return list(set(deps)) # Remove duplicates

    def __repr__(self) -> str:
        return f"{super().__repr__()}, input_element={self.input_element.name!r}, smoothing_time={self.smoothing_time.name!r}, initial_value={self.initial_value})"


class Table(Element):
    """
    An element that performs a lookup from a table (functional relationship)
    using linear interpolation.
    """
    def __init__(self, name: str, input_element: Element, points: Sequence[Tuple[float, float]]):
        super().__init__(name)
        self.input_element = input_element
        # Ensure points are sorted by x-value
        self.points = sorted(points, key=lambda p: p[0])

        if len(self.points) < 2:
            raise ValueError("Table must have at least two points for interpolation.")

    def compute(self, context: dict[str, Any]) -> float:
        input_val = self.input_element.compute(context)

        # Handle extrapolation (return first/last y-value)
        if input_val <= self.points[0][0]:
            return self.points[0][1]
        if input_val >= self.points[-1][0]:
            return self.points[-1][1]

        # Find the interval for interpolation
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i+1]

            if x1 <= input_val <= x2:
                # Linear interpolation
                if x1 == x2: # Avoid division by zero if two points have same x-value
                    return (y1 + y2) / 2 # Or just y1, depending on desired behavior
                
                return y1 + (input_val - x1) * (y2 - y1) / (x2 - x1)
        
        # This part should ideally not be reached due to extrapolation checks
        return 0.0 # Fallback

    @property
    def dependencies(self) -> list[Element]:
        deps = [self.input_element]
        if hasattr(self.input_element, 'dependencies'):
            deps.extend(self.input_element.dependencies)
        return list(set(deps)) # Remove duplicates

    def __repr__(self) -> str:
        return f"{super().__repr__()}, input_element={self.input_element.name!r}, points={self.points!r})"


class IfThenElse(Element):
    """
    An element that represents conditional logic.
    If condition > 0, returns the true_element's value, else returns the false_element's value.
    """
    def __init__(self, name: str, condition: Element, true_element: Element, false_element: Element):
        super().__init__(name)
        self.condition = condition
        self.true_element = true_element
        self.false_element = false_element

    def compute(self, context: dict[str, Any]) -> float:
        condition_val = self.condition.compute(context)
        if condition_val > 0:
            return self.true_element.compute(context)
        else:
            return self.false_element.compute(context)

    @property
    def dependencies(self) -> list[Element]:
        deps = [self.condition, self.true_element, self.false_element]
        if hasattr(self.condition, 'dependencies'):
            deps.extend(self.condition.dependencies)
        if hasattr(self.true_element, 'dependencies'):
            deps.extend(self.true_element.dependencies)
        if hasattr(self.false_element, 'dependencies'):
            deps.extend(self.false_element.dependencies)
        return list(set(deps))

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, condition={self.condition.name!r}, "
                f"true_element={self.true_element.name!r}, false_element={self.false_element.name!r})")


class Min(Element):
    """
    An element that returns the minimum of its input elements.
    """
    def __init__(self, name: str, *input_elements: Element):
        super().__init__(name)
        if not input_elements:
            raise ValueError("Min element must have at least one input element.")
        self.input_elements = input_elements

    def compute(self, context: dict[str, Any]) -> float:
        return min(el.compute(context) for el in self.input_elements)

    @property
    def dependencies(self) -> list[Element]:
        deps = []
        for el in self.input_elements:
            deps.append(el)
            if hasattr(el, 'dependencies'):
                deps.extend(el.dependencies)
        return list(set(deps))

    def __repr__(self) -> str:
        input_names = ", ".join(el.name for el in self.input_elements)
        return f"{super().__repr__()}, inputs=[{input_names}])"


class Max(Element):
    """
    An element that returns the maximum of its input elements.
    """
    def __init__(self, name: str, *input_elements: Element):
        super().__init__(name)
        if not input_elements:
            raise ValueError("Max element must have at least one input element.")
        self.input_elements = input_elements

    def compute(self, context: dict[str, Any]) -> float:
        return max(el.compute(context) for el in self.input_elements)

    @property
    def dependencies(self) -> list[Element]:
        deps = []
        for el in self.input_elements:
            deps.append(el)
            if hasattr(el, 'dependencies'):
                deps.extend(el.dependencies)
        return list(set(deps))

    def __repr__(self) -> str:
        input_names = ", ".join(el.name for el in self.input_elements)
        return f"{super().__repr__()}, inputs=[{input_names}])"


class Pulse(Element):
    """
    An element that generates a pulse (a temporary burst) of a given magnitude.
    """
    def __init__(self, name: str, start_time: Element, duration: Element, magnitude: Element):
        super().__init__(name)
        self.start_time = start_time
        self.duration = duration
        self.magnitude = magnitude

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context.get('time')
        start = self.start_time.compute(context)
        dur = self.duration.compute(context)
        mag = self.magnitude.compute(context)

        if start <= current_time < start + dur:
            return mag
        return 0.0

    @property
    def dependencies(self) -> list[Element]:
        deps = [self.start_time, self.duration, self.magnitude]
        for el in deps:
            if hasattr(el, 'dependencies'):
                deps.extend(el.dependencies)
        return list(set(deps))

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, start_time={self.start_time.name!r}, "
                f"duration={self.duration.name!r}, magnitude={self.magnitude.name!r})")


class Step(Element):
    """
    An element that generates a step change in value at a specified start_time.
    """
    def __init__(self, name: str, start_time: float|Element, before_value: float|Element, after_value: float|Element):
        super().__init__(name)
        self.start_time = _to_element(start_time)
        self.before_value = _to_element(before_value)
        self.after_value = _to_element(after_value)

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context.get('time')
        start = self.start_time.compute(context)

        if current_time < start:
            return self.before_value.compute(context)
        else:
            return self.after_value.compute(context)

    @property
    def dependencies(self) -> list[Element]:
        deps = [self.start_time, self.before_value, self.after_value]
        for el in deps:
            if hasattr(el, 'dependencies'):
                deps.extend(el.dependencies)
        return list(set(deps))

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, start_time={self.start_time.name!r}, "
                f"before_value={self.before_value.name!r}, after_value={self.after_value.name!r})")


class Ramp(Element):
    """
    An element that generates a linearly increasing (or decreasing) value over a period.
    """
    def __init__(self, name: str, start_time: Element, end_time: Element, slope: Element, initial_value: Element):
        super().__init__(name)
        self.start_time = start_time
        self.end_time = end_time
        self.slope = slope
        self.initial_value = initial_value

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context.get('time', 0.0)
        start = self.start_time.compute(context)
        end = self.end_time.compute(context)
        slp = self.slope.compute(context)
        initial = self.initial_value.compute(context)

        if current_time < start:
            return initial
        elif start <= current_time <= end:
            return initial + slp * (current_time - start)
        else: # current_time > end
            return initial + slp * (end - start) # Hold the value at end_time

    @property
    def dependencies(self) -> list[Element]:
        deps = [self.start_time, self.end_time, self.slope, self.initial_value]
        for el in deps:
            if hasattr(el, 'dependencies'):
                deps.extend(el.dependencies)
        return list(set(deps))

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, start_time={self.start_time.name!r}, "
                f"end_time={self.end_time.name!r}, slope={self.slope.name!r}, "
                f"initial_value={self.initial_value.name!r})")


class Initial(Element):
    """
    An element that returns the initial value of an input element.
    This is particularly useful for Stocks.
    """
    def __init__(self, name: str, input_element: Element):
        super().__init__(name)
        self.input_element = input_element

    def compute(self, context: dict[str, Any]) -> float:
        # For Stocks, return their initial_value.
        # For other elements, their "initial value" might be their compute() at t=0
        # If input_element has an initial_value attribute (like Stock), use it.
        if hasattr(self.input_element, 'initial_value'):
            return self.input_element.initial_value
        
        # Otherwise, compute its value at time 0.0
        # Need to create a context for time 0.0
        # This assumes the input_element's compute method can handle this
        initial_context = {
            "time": 0.0,
            "state": {el.name: el.initial_value for el in self.model.stocks.values()} if self.model else {}, # Pass initial stock states
            "history_lookup": lambda name, delay_time_param: 0.0, # History is empty at t=0 for initial compute
            "dt": context.get('dt', 0.0) # Pass dt if available
        }
        # This recursive call to compute can be problematic if the element itself relies on history
        # for its initial computation. For simplicity, we assume compute at t=0 works without history
        # or that initial_value attribute is preferred.
        return self.input_element.compute(initial_context)

    @property
    def dependencies(self) -> list[Element]:
        deps = [self.input_element]
        if hasattr(self.input_element, 'dependencies'):
            deps.extend(self.input_element.dependencies)
        return list(set(deps))

    def __repr__(self) -> str:
        return f"{super().__repr__()}, input_element={self.input_element.name!r})"

