from __future__ import annotations
from typing import TYPE_CHECKING, Any, Sequence, Tuple

from mead.core import Element, DependenciesProperty
from mead.stock import Stock
from mead.utils import as_element

if TYPE_CHECKING:
    from mead.model import Model

class Delay(DependenciesProperty, Element):
    """
    An element that returns a delayed value of an input Stock.
    Requires the model to manage history.
    """
    _element_attrs = ["input_stock", "delay_time"]

    def __init__(self, name: str, input_stock: Element, delay_time: float | Element):
        super().__init__(name)
        self.input_stock = input_stock
        self.delay_time = as_element(delay_time)

    def compute(self, context: dict[str, Any]) -> float:
        history_lookup = context.get('history_lookup')
        if not history_lookup:
            raise RuntimeError("Delay element requires a 'history_lookup' function in the context.")
        
        computed_delay_time = self.delay_time.compute(context) # Compute the value of delay_time
        return history_lookup(self.input_stock.name, computed_delay_time)

    def __repr__(self) -> str:
        return f"{super().__repr__()}, input_stock={self.input_stock.name!r}, delay_time={self.delay_time})"

class Smooth(DependenciesProperty, Element):
    """
    An element that computes an exponential smooth of an input.
    smooth_value(t) = smooth_value(t-dt) + (dt / smoothing_time) * (input_value(t) - smooth_value(t-dt))
    Requires the model to manage history of this smooth element itself.
    """
    _element_attrs = ["target_value", "smoothing_time", "initial_value"]

    def __init__(self, 
                 name: str, 
                 target_value: float | Element, 
                 smoothing_time: float | Element, 
                 initial_value: float | Element = 0.0):
        super().__init__(name)
        self.target_value = as_element(target_value)
        self.smoothing_time = as_element(smoothing_time)
        self.initial_value = as_element(initial_value)

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context.get('time')
        if current_time == 0.0:
            return self.initial_value.compute(context)
            
        history_lookup = context.get('history_lookup')
        dt = context.get('dt')

        if not history_lookup or dt is None:
            raise RuntimeError("Smooth element requires 'history_lookup' and 'dt' in the context.")

        input_val = self.target_value.compute(context)
        smoothing_time_val = self.smoothing_time.compute(context)

        # Get the previous value of THIS smooth element
        previous_smooth_val = history_lookup(self.name, dt)
        
        if smoothing_time_val == 0: # Avoid division by zero
            return input_val
        
        # Exponential smoothing formula
        return previous_smooth_val + (dt / smoothing_time_val) * (input_val - previous_smooth_val)

    def __repr__(self) -> str:
        return f"{super().__repr__()}, input_element={self.target_value.name!r}, smoothing_time={self.smoothing_time.name!r}, initial_value={self.initial_value})"


class Table(DependenciesProperty, Element):
    """
    An element that performs a lookup from a table (functional relationship)
    using linear interpolation.
    """
    _element_attrs = ["input_element"]

    def __init__(self, 
                 name: str, 
                 input: float | Element, 
                 points: Sequence[Tuple[float, float]]):
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
            x2, y2 = self.points[i+1]

            if x1 <= input_val <= x2:
                # Linear interpolation
                if x1 == x2: # Avoid division by zero 
                    return (y1 + y2) / 2 
                
                return y1 + (input_val - x1) * (y2 - y1) / (x2 - x1)
        
        return 0.0 # Fallback

    def __repr__(self) -> str:
        return f"{super().__repr__()}, input_element={self.input_element.name!r}, points={self.points!r})"


class IfThenElse(DependenciesProperty, Element):
    """
    An element that represents conditional logic.
    If condition > 0, returns the true_element's value, else returns the false_element's value.
    """
    _element_attrs = ["condition", "true_element", "false_element"]

    def __init__(self, 
                 name: str, 
                 condition: float | Element, 
                 true_element: float | Element, 
                 false_element: float | Element):
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

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, condition={self.condition.name!r}, "
                f"true_element={self.true_element.name!r}, false_element={self.false_element.name!r})")


class Min(DependenciesProperty, Element):
    """
    An element that returns the minimum of its input elements.
    """
    _element_attrs = ["input_elements"] # input_elements is a list of Elements

    def __init__(self, name: str, *input_elements: float | Element):
        super().__init__(name)
        if not input_elements:
            raise ValueError("Min element must have at least one input element.")
        self.input_elements = [as_element(i) for i in input_elements]

    def compute(self, context: dict[str, Any]) -> float:
        return min(el.compute(context) for el in self.input_elements)

    def __repr__(self) -> str:
        input_names = ", ".join(el.name for el in self.input_elements)
        return f"{super().__repr__()}, inputs=[{input_names}])"


class Max(DependenciesProperty, Element):
    """
    An element that returns the maximum of its input elements.
    """
    _element_attrs = ["input_elements"] # input_elements is a list of Elements

    def __init__(self, name: str, *input_elements: float | Element):
        super().__init__(name)
        if not input_elements:
            raise ValueError("Max element must have at least one input element.")
        self.input_elements = [as_element(i) for i in input_elements]

    def compute(self, context: dict[str, Any]) -> float:
        return max(el.compute(context) for el in self.input_elements)

    def __repr__(self) -> str:
        input_names = ", ".join(el.name for el in self.input_elements)
        return f"{super().__repr__()}, inputs=[{input_names}])"


class Pulse(DependenciesProperty, Element):
    """
    An element that generates a pulse (a temporary burst) of a given magnitude.
    """
    _element_attrs = ["start_time", "duration", "magnitude"]

    def __init__(self, 
                 name: str, 
                 start_time: float | Element, 
                 duration: float | Element, 
                 ammount: float | Element):
        super().__init__(name)
        self.start_time = as_element(start_time)
        self.duration = as_element(duration)
        self.magnitude = as_element(ammount)

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context.get('time')
        start = self.start_time.compute(context)
        dur = self.duration.compute(context)
        mag = self.magnitude.compute(context)

        if start <= current_time < start + dur:
            return mag
        return 0.0

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, start_time={self.start_time.name!r}, "
                f"duration={self.duration.name!r}, magnitude={self.magnitude.name!r})")


class Step(DependenciesProperty, Element):
    """
    An element that generates a step change in value at a specified start_time.
    """
    _element_attrs = ["start_time", "before_value", "after_value"]

    def __init__(self, name: str, start_time: float|Element, before_value: float|Element, after_value: float|Element):
        super().__init__(name)
        self.start_time = as_element(start_time)
        self.before_value = as_element(before_value)
        self.after_value = as_element(after_value)

    def compute(self, context: dict[str, Any]) -> float:
        current_time = context.get('time')
        start = self.start_time.compute(context)

        if current_time < start:
            return self.before_value.compute(context)
        else:
            return self.after_value.compute(context)

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, start_time={self.start_time.name!r}, "
                f"before_value={self.before_value.name!r}, after_value={self.after_value.name!r})")


class Ramp(DependenciesProperty, Element):
    """
    An element that generates a linearly increasing (or decreasing) value over a period.
    """
    _element_attrs = ["start_time", "end_time", "slope", "initial_value"]

    def __init__(
            self, 
            name: str, 
            start_time: float | Element, 
            end_time: float | Element, 
            ammount: float | Element, 
            initial_value: float | Element = 0.0):
        super().__init__(name)
        self.start_time = as_element(start_time)
        self.end_time = as_element(end_time)
        self.slope = as_element(ammount)
        self.initial_value = as_element(initial_value)

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
        else:
            return initial + slp * (end - start) # Hold the value at end_time

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, start_time={self.start_time.name!r}, "
                f"end_time={self.end_time.name!r}, slope={self.slope.name!r}, "
                f"initial_value={self.initial_value.name!r})")


class Delay2(DependenciesProperty, Element):
    """
    A second-order exponential delay element, implemented as a chain of two Smooth components.
    """
    _element_attrs = ["input_element", "delay_time", "initial_value", "smooth1", "smooth2"]

    def __init__(
        self,
        name: str,
        input_element: float | Element,
        delay_time: float | Element,
        initial_value: float | Element = 0.0
    ):
        super().__init__(name)
        self.input_element = as_element(input_element)
        self.delay_time = as_element(delay_time)
        self.initial_value = as_element(initial_value)

        # The effective smoothing time for each stage of a second-order delay
        # is delay_time / 2.0
        smoothing_time_per_stage = as_element(self.delay_time / 2.0)

        # Chain two Smooth components
        self.smooth1 = Smooth(f"{name}_smooth1", self.input_element, smoothing_time_per_stage, self.initial_value)
        self.smooth2 = Smooth(f"{name}_smooth2", self.smooth1, smoothing_time_per_stage, self.initial_value)

    def compute(self, context: dict[str, Any]) -> float:
        # The output of Delay2 is the output of the final Smooth component
        return self.smooth2.compute(context)

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, input_element={self.input_element.name!r}, "
                f"delay_time={self.delay_time.name!r}, initial_value={self.initial_value.name!r})")


class Delay3(DependenciesProperty, Element):
    """
    A third-order exponential delay element, implemented as a chain of three Smooth components.
    """
    _element_attrs = ['input_element', 'delay_time', 'initial_value', 'smooth1', 'smooth2', 'smooth3']

    def __init__(
        self,
        name: str,
        input_element: float | Element,
        delay_time: float | Element,
        initial_value: float | Element = 0.0
    ):
        super().__init__(name)
        self.input_element = as_element(input_element)
        self.delay_time = as_element(delay_time)
        self.initial_value = as_element(initial_value)

        # The effective smoothing time for each stage of a third-order delay
        # is delay_time / 3.0
        smoothing_time_per_stage = as_element(self.delay_time / 3.0)

        # Chain three Smooth components
        self.smooth1 = Smooth(f"{name}_smooth1", self.input_element, smoothing_time_per_stage, self.initial_value)
        self.smooth2 = Smooth(f"{name}_smooth2", self.smooth1, smoothing_time_per_stage, self.initial_value)
        self.smooth3 = Smooth(f"{name}_smooth3", self.smooth2, smoothing_time_per_stage, self.initial_value)

    def compute(self, context: dict[str, Any]) -> float:
        # The output of Delay3 is the output of the final Smooth component
        return self.smooth3.compute(context)

    def __repr__(self) -> str:
        return (f"{super().__repr__()}, input_element={self.input_element.name!r}, "
                f"delay_time={self.delay_time.name!r}, initial_value={self.initial_value.name!r})")


class Initial(DependenciesProperty, Element):
    """
    An element that returns the initial value of an input element.
    """
    _element_attrs = ['input_element']

    def __init__(self, name: str, input_element: Element):
        super().__init__(name)
        self.input_element = input_element

    def compute(self, context: dict[str, Any]) -> float:
        if isinstance(self.input_element, Stock):
            return self.input_element.initial_value

        # compute at t=0
        initial_context = {
            "time": 0.0,
            "state": {el.name: el.initial_value for el in self.model.stocks.values()} if self.model else {},
            "history_lookup": lambda name, delay_time_param: 0.0,
            "dt": context.get('dt', 0.0)
        }
        return self.input_element.compute(initial_context)

    def __repr__(self) -> str:
        return f"{super().__repr__()}, input_element={self.input_element.name!r})"

