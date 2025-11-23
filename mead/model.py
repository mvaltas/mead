import pandas as pd
from typing import Literal, Type, Any, Callable, List, Optional
from pathlib import Path # Import Path for file operations
import matplotlib.pyplot as plt # Import matplotlib for plotting

from mead.core import Element, Constant
from mead.components import Delay # Import Delay from its new location
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

    def _lookup_history(self, name: str, current_sim_time: float, delay_time: float) -> float:
        """
        Looks up the historical value of a named element at a specific time in the past.
        """
        if not self._history:
            return 0.0 # No history yet, return 0.0

        target_time = current_sim_time - delay_time
        
        # If target time is before the very first recorded state, return 0.0
        # This handles cases where delay_time is large or current_sim_time is very small.
        if target_time < self._history[0][0]:
            return 0.0

        # Iterate in reverse to find the closest historical state at or before target_time
        # _history stores (time, element_values_at_that_time)
        for history_time, history_values in reversed(self._history):
            if history_time <= target_time:
                return history_values.get(name, 0.0)
        
        # Should not be reached if target_time >= self._history[0][0] and history is not empty.
        return 0.0

    def _create_element_context(self, time: float, state: dict[str, float]) -> dict[str, Any]:
        """Helper to create the context dictionary for element compute methods."""
        return {
            "time": time,
            "state": state,
            "history_lookup": lambda name, delay_time_val: self._lookup_history(name, time, delay_time_val),
            "dt": self.dt
        }

    def _compute_derivatives(self, time: float, state: dict[str, float]) -> dict[str, float]:
        """Calculates the net change for all stocks at a given time and state."""
        derivatives = {}
        context = self._create_element_context(time, state)

        for stock in self.stocks.values():
            inflow_rate = sum(flow.compute(context) for flow in stock.inflows)
            outflow_rate = sum(flow.compute(context) for flow in stock.outflows)
            derivatives[stock.name] = inflow_rate - outflow_rate
        return derivatives

    def run(self, duration: float, method: IntegrationMethod = "euler") -> pd.DataFrame:
        solver = self._solvers[method]()
        self._history = [] # Reset history for each run
        
        state = {s.name: s.initial_value for s in self.stocks.values()}
        
        num_steps = int(duration / self.dt)
        times = [i * self.dt for i in range(num_steps + 1)]
        results_list = []

        for i, time in enumerate(times):
            context_for_elements = self._create_element_context(time, state)
            
            # compute or retrieve stock value
            current_element_values = {name: (state[name] if name in state else element.compute(context_for_elements)) 
                                      for name, element in self.elements.items()}

            self._history.append((time, current_element_values.copy()))
            results_list.append({'time': time, **current_element_values})

            if i < num_steps:
                state = solver.step(time, self.dt, state, self._compute_derivatives)

        return pd.DataFrame(results_list).set_index("time")

    def plot(self, results: pd.DataFrame, columns: Optional[List[str]] = None, save_path: Optional[Path] = None):
        """
        Generates a time-series line plot of the simulation results.

        Args:
            results: The DataFrame returned by the `run` method.
            columns: A list of column names to plot. If None, all columns except 'time' are plotted.
            save_path: If provided, the plot will be saved to this file path.
                       Otherwise, plt.show() will be called.
        """
        if columns is None:
            # Exclude 'time' from columns if it's there
            plot_columns = [col for col in results.columns if col != 'time']
        else:
            plot_columns = [col for col in columns if col in results.columns]

        if not plot_columns:
            print("No columns to plot.")
            return

        fig, ax = plt.subplots(figsize=(10, 6))
        
        for col in plot_columns:
            ax.plot(results.index, results[col], label=col)

        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.set_title(f"Simulation Results for {self.name}")
        ax.legend()
        ax.grid(True)

        if save_path:
            plt.savefig(save_path)
            plt.close(fig) # Close the figure to free up memory
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
