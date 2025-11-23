"""
System Thinking - A composable Python framework for System Dynamics modeling.

This package provides simple building blocks for creating and simulating
system dynamics models including stocks, flows, and feedback loops.
"""

"""
System Thinking - A composable Python framework for System Dynamics modeling.
"""

from .core import Element, Constant, Equation, Auxiliary
from .components import Delay, Smooth, Table, IfThenElse, Min, Max, Pulse, Step, Ramp, Initial # Import all new components
from .stock import Stock
from .flow import Flow, goal_flow
from .model import Model

__version__ = "0.2.0"

__all__ = [
    "Element",
    "Constant",
    "Equation",
    "Auxiliary",
    "Delay", # Now from components
    "Smooth", # New component
    "Table", # New component
    "IfThenElse", # New component
    "Min", # New component
    "Max", # New component
    "Pulse", # New component
    "Step", # New component
    "Ramp", # New component
    "Initial", # New component
    "Stock",
    "Flow",
    "goal_flow",
    "Model",
]

