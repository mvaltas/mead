"""Model represents a complete system dynamics simulation."""

import pandas as pd
import matplotlib.pyplot as plt
from typing import Literal, Callable

from .stock import Stock
from .solver import Solver, EulerSolver, RK4Solver


IntegrationMethod = Literal["euler", "rk4"]


class Model:
    """
    A Model contains stocks and flows and runs simulations.

    The model uses numerical integration to simulate the system over time.
    """

    def __init__(self, name: str, dt: float = 0.25):
        """
        Initialize a model.

        Args:
            name: Model name
            dt: Time step for integration (default: 0.25)
        """
        self.name = name
        self.dt = dt
        self._stocks: dict[str, Stock] = {}
        self._solvers: dict[str, Solver] = {
            "euler": EulerSolver(),
            "rk4": RK4Solver(),
        }
        self._history: list[tuple[float, dict[str, float]]] = []
    
    def add_stock(self, stock: Stock) -> None:
        if stock.name in self._stocks:
            raise ValueError(f"Stock '{stock.name}' already exists in model")
        self._stocks[stock.name] = stock
    
    def reset(self) -> None:
        self._history = []
        for stock in self._stocks.values():
            stock.reset()
    
    def _get_state(self) -> dict[str, float]:
        return {name: stock.value for name, stock in self._stocks.items()}

    def _lookup_history(self, name: str, delay: float) -> float:
        """Finds a value in the history."""
        target_time = self._history[-1][0] - delay
        if target_time < 0:
            return 0.0 # Or initial value?

        # Simple lookup, could be improved with interpolation
        for time, state in reversed(self._history):
            if time <= target_time:
                return state.get(name, 0.0)
        return 0.0

    def _compute_derivatives(self, time: float, state: dict[str, float]) -> dict[str, float]:
        context = {
            "time": time,
            "state": state,
            "history": self._lookup_history
        }
        return {name: stock.net_flow(context) for name, stock in self._stocks.items()}

    def _step(self, time: float, method: IntegrationMethod) -> None:
        if method not in self._solvers:
            raise ValueError(f"Unknown integration method: {method}")

        solver = self._solvers[method]
        state = self._get_state()
        new_state = solver.step(time, self.dt, state, self._compute_derivatives)

        for name, stock in self._stocks.items():
            stock.set_value(new_state[name])

    def run(self, duration: float, method: IntegrationMethod = "euler") -> pd.DataFrame:
        self.reset()

        num_steps = int(duration / self.dt) + 1
        times = [i * self.dt for i in range(num_steps)]
        results = {"time": times, **{name: [] for name in self._stocks}}

        for i, time in enumerate(times):
            # Record current state at the beginning of the step
            current_state = self._get_state()
            self._history.append((time, current_state))
            
            for name, stock in self._stocks.items():
                results[name].append(stock.value)

            if i < num_steps - 1:
                self._step(time, method)

        return pd.DataFrame(results)
    
    def plot(self, results: pd.DataFrame, *stock_names: str) -> None:
        """
        Plot simulation results.
        
        Args:
            results: DataFrame from run()
            stock_names: Names of stocks to plot (plots all if none specified)
        """
        if not stock_names:
            stock_names = tuple(name for name in results.columns if name != "time")
        
        plt.figure(figsize=(10, 6))
        for name in stock_names:
            if name in results.columns:
                plt.plot(results["time"], results[name], label=name, linewidth=2)
        
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.title(f"{self.name} - Simulation Results")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
