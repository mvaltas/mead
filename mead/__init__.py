"""
System Thinking - A composable Python framework for System Dynamics modeling.

This package provides simple building blocks for creating and simulating
system dynamics models including stocks, flows, and feedback loops.
"""

"""
System Thinking - A composable Python framework for System Dynamics modeling.
"""

from .core import Element, Constant, Equation, Auxiliary, Delay
from .stock import Stock
from .flow import Flow, goal_flow
from .model import Model

__version__ = "0.2.0"

__all__ = [
    "Element",
    "Constant",
    "Equation",
    "Auxiliary",
    "Delay",
    "Stock",
    "Flow",
    "goal_flow",
    "Model",
]

