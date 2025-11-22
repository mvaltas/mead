"""
System Thinking - A composable Python framework for System Dynamics modeling.

This package provides simple building blocks for creating and simulating
system dynamics models including stocks, flows, and feedback loops.
"""

from .stock import Stock
from .flow import Flow, constant, fractional, table_lookup
from .model import Model

__version__ = "0.1.0"

__all__ = [
    "Stock",
    "Flow",
    "Model",
    "constant",
    "fractional",
    "table_lookup",
]
