"""Integration solvers for system dynamics models."""

from abc import ABC, abstractmethod
from typing import Callable


class Solver(ABC):
    """
    Abstract base class for numerical integration solvers.
    
    Solvers implement different numerical integration methods (Euler, RK4, etc.)
    to advance the system state forward in time.
    """
    
    @abstractmethod
    def step(
        self,
        time: float,
        dt: float,
        state: dict[str, float],
        compute_derivatives: Callable[[float, dict[str, float]], dict[str, float]],
    ) -> dict[str, float]:
        """
        Perform one integration step.
        
        Args:
            time: Current simulation time
            dt: Time step size
            state: Current state (stock name -> value)
            compute_derivatives: Function to compute derivatives at given time and state
            
        Returns:
            New state after one time step
        """
        pass


class EulerSolver(Solver):
    """
    Euler method solver (first-order).
    
    Simple and fast but less accurate. Good for teaching and non-stiff systems.
    Formula: x(t+dt) = x(t) + dx/dt * dt
    """
    
    def step(
        self,
        time: float,
        dt: float,
        state: dict[str, float],
        compute_derivatives: Callable[[float, dict[str, float]], dict[str, float]],
    ) -> dict[str, float]:
        """Perform one Euler integration step."""
        derivatives = compute_derivatives(time, state)
        return {name: state[name] + derivatives[name] * dt for name in state}


class RK4Solver(Solver):
    """
    Runge-Kutta 4th order solver.
    
    More accurate than Euler, especially for stiff systems.
    Uses weighted average of four derivative evaluations per step.
    """
    
    def step(
        self,
        time: float,
        dt: float,
        state: dict[str, float],
        compute_derivatives: Callable[[float, dict[str, float]], dict[str, float]],
    ) -> dict[str, float]:
        """Perform one RK4 integration step."""
        half_dt = dt / 2

        k1 = compute_derivatives(time, state)
        k2 = compute_derivatives(time + half_dt, self._advance_state(state, k1, half_dt))
        k3 = compute_derivatives(time + half_dt, self._advance_state(state, k2, half_dt))
        k4 = compute_derivatives(time + dt, self._advance_state(state, k3, dt))

        new_state = {}
        for name in state:
            weighted_derivative = (k1[name] + 2*k2[name] + 2*k3[name] + k4[name]) / 6
            new_state[name] = state[name] + weighted_derivative * dt

        return new_state
    
    @staticmethod
    def _advance_state(
        state: dict[str, float],
        derivatives: dict[str, float],
        dt: float
    ) -> dict[str, float]:
        """Advance state by dt using given derivatives."""
        return {name: state[name] + derivatives[name] * dt for name in state}

