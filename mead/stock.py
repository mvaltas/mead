from __future__ import annotations
from typing import TYPE_CHECKING
from mead.core import Element

if TYPE_CHECKING:
    from mead.flow import Flow


class Stock(Element):
    """
    A Stock represents a state variable that accumulates over time.
    Stocks are changed by flows.
    """

    def __init__(self, name: str, initial_value: float = 0.0):
        super().__init__(name)
        self.initial_value = initial_value
        self.inflows: list[Flow] = []
        self.outflows: list[Flow] = []

    def add_inflow(self, flow: Flow) -> None:
        """Add a flow that increases this stock."""
        self.inflows.append(flow)

    def add_outflow(self, flow: Flow) -> None:
        """Add a flow that decreases this stock."""
        self.outflows.append(flow)
