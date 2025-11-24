import pandas as pd
from typing import Literal, Type, Any, List, Optional
from pathlib import Path 
import matplotlib.pyplot as plt

from mead.core import Element, DependenciesProperty
from mead.stock import Stock
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
        """Adds one or more elements to the model.

        Args:
            elements: Elements that participate in this model simulation.
        """
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
            return 0.0 

        target_time = current_sim_time - delay_time
        
        # default to 0.0 if access time precedes history
        if target_time < self._history[0][0]:
            return 0.0

        for history_time, history_values in reversed(self._history):
            if history_time <= target_time:
                return history_values.get(name, 0.0)
        
        return 0.0 # fallback

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

    def _collect_all_elements(self) -> dict[str, Element]:
        """
        Recursively collects all unique elements in the model's computation graph,
        starting from the top-level elements added via model.add().
        """
        all_elements: dict[str, Element] = {}
        to_process: list[Element] = list(self.elements.values())
        
        while to_process:
            current_element = to_process.pop()
            if current_element.name not in all_elements:
                all_elements[current_element.name] = current_element
                # explicit dependencies
                if hasattr(current_element, 'dependencies'):
                    for dep in current_element.dependencies:
                        if isinstance(dep, Element) and dep.name not in all_elements:
                            to_process.append(dep)
                
                # collect internal dependencies
                if hasattr(current_element, '__dict__'):
                    for attr_value in current_element.__dict__.values():
                        if isinstance(attr_value, Element) and attr_value.name not in all_elements:
                            to_process.append(attr_value)
                        elif isinstance(attr_value, list):
                            for item in attr_value:
                                if isinstance(item, Element) and item.name not in all_elements:
                                    to_process.append(item)
        return all_elements

    def run(self, duration: float, method: IntegrationMethod = "euler") -> pd.DataFrame:
        solver = self._solvers[method]()
        self._history = [] # Reset history for each run
        
        # Collect all elements in the computation graph
        all_elements_to_compute = self._collect_all_elements()
        
        # Initialize state with initial values of all stocks
        state = {s.name: s.initial_value for s in self.stocks.values()}
        
        num_steps = int(duration / self.dt)
        times = [i * self.dt for i in range(num_steps + 1)]
        results_list = []

        for i, time in enumerate(times):
            context_for_elements = self._create_element_context(time, state)
            
            # Compute values for all collected elements
            current_element_values = {}
            for name, element in all_elements_to_compute.items():
                if name in state: # If it's a stock, its value is in the state
                    current_element_values[name] = state[name]
                else: # Otherwise, compute its value
                    current_element_values[name] = element.compute(context_for_elements)

            self._history.append((time, current_element_values.copy()))
            results_list.append({'time': time, **current_element_values})

            if i < num_steps:
                state = solver.step(time, self.dt, state, self._compute_derivatives)

        return pd.DataFrame(results_list).set_index("time")

    def plot(self, 
             results: pd.DataFrame, 
             columns: Optional[List[str]] = None, 
             labels: tuple[str,str] = ('Time', 'Value'),
             save_path: Optional[str | Path] = None,
             ):
        """
        Quick shortcut to plot results from simulation, more robust plotting prefer
        using `matplotlib` directly.

        Args:
            results: The DataFrame returned by the `run` method.
            columns: A list of column names to plot. If None, all columns are plotted.
            labels: A tuple in the form (x_label, y_label), defaults to *Time x Value*
            save_path: If provided, the plot is saved; otherwise, it's displayed.
        """
        if columns is None:
            columns = [col for col in results.columns if col != 'time']
        
        if not columns: 
            print("No columns to plot.")
            return

        fig, ax1 = plt.subplots(figsize=(12, 7))
        
        colors = plt.cm.get_cmap('Dark2', len(columns))
        line1_handles = []
        for i, col in enumerate(columns):
            line, = ax1.plot(results.index, results[col], label=col, color=colors(i))
            line1_handles.append(line)

        ax1.set_xlabel(labels[0])
        ax1.set_ylabel(labels[1])
        ax1.grid(True)

        ax1.legend(loc='best')
            
        ax1.set_title(f"Simulation Results for {self.name}")

        if save_path:
            plt.savefig(Path(save_path))
            plt.close(fig)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
