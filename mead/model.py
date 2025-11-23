import pandas as pd
from typing import Literal, Type, Any, Callable
from mead.core import Element, Constant, Delay
from mead.stock import Stock
from mead.flow import Flow
from .solver import Solver, EulerSolver, RK4Solver

IntegrationMethod = Literal["euler", "rk4"]

class Model:
    """
    A Model contains all the elements of a system dynamics simulation
    and runs the simulation over time.
    """
    def __init__(self, name: str, dt: float = 0.25):
        self.name = name
        self.dt = dt
        self.elements: dict[str, Element] = {}
        self.stocks: dict[str, Stock] = {}
        self._solvers: dict[str, Type[Solver]] = {
            "euler": EulerSolver,
            "rk4": RK4Solver,
        }
        self._history: list[tuple[float, dict[str, float]]] = []

    def add(self, *elements: Element):
        """Adds one or more elements to the model."""
        for element in elements:
            if element.name in self.elements:
                raise ValueError(f"Element '{element.name}' already exists in model")
            self.elements[element.name] = element
            element.model = self
            if isinstance(element, Stock):
                self.stocks[element.name] = element

    def _lookup_history(self, name: str, delay_time: float) -> float:
        """
        Looks up the historical value of a named stock.
        Only works for Stocks.
        """
        if not self._history:
            return 0.0 # Or raise error/return initial_value

        current_time = self._history[-1][0]
        target_time = current_time - delay_time
        
        if target_time < 0:
            return 0.0 # Return 0.0 if the target time is before the simulation started

        # Iterate in reverse to find the closest historical state
        for time, state in reversed(self._history):
            if time <= target_time:
                return state.get(name, 0.0)
        
        # If no history point is found for target_time (e.g., target_time is very early)
        return self._history[0][1].get(name, 0.0) if self._history else 0.0


    def _compute_derivatives(self, time: float, state: dict[str, float]) -> dict[str, float]:
        """Calculates the net change for all stocks at a given time and state."""
        derivatives = {}
        # Create a richer context to pass to element.compute methods
        context = {
            "time": time,
            "state": state,
            "history_lookup": self._lookup_history
        }

        for stock in self.stocks.values():
            # Pass the richer context to the flow's compute method
            inflow_rate = sum(flow.compute(context) for flow in stock.inflows)
            outflow_rate = sum(flow.compute(context) for flow in stock.outflows)
            derivatives[stock.name] = inflow_rate - outflow_rate
        return derivatives

    def run(self, duration: float, method: IntegrationMethod = "euler") -> pd.DataFrame:
        """Runs the simulation."""
        solver = self._solvers[method]()
        self._history = [] # Reset history for each run
        
        # Initialize state from stocks
        state = {s.name: s.initial_value for s in self.stocks.values()}
        
        num_steps = int(duration / self.dt)
        times = [i * self.dt for i in range(num_steps + 1)]
        results_list = []

        for i, time in enumerate(times):
            # Record current state and time for history lookup
            self._history.append((time, state.copy()))
            results_list.append({'time': time, **state})

            if i < num_steps:
                state = solver.step(time, self.dt, state, self._compute_derivatives)

        return pd.DataFrame(results_list).set_index("time")
