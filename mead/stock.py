from .flow import Flow


class Stock:
    """
    A Stock represents a state variable that accumulates over time.
    
    Stocks are changed by flows (inflows increase, outflows decrease).
    """

    def __init__(self, name: str, initial_value: float):
        """
        Initialize a stock.
        
        Args:
            name: Unique identifier for the stock
            initial_value: Starting value at time 0
        """
        self.name = name
        self.initial_value = initial_value
        self._current_value = initial_value
        self._inflows: list[Flow] = []
        self._outflows: list[Flow] = []
    
    def add_inflow(self, flow: Flow) -> None:
        """Add a flow that increases this stock."""
        self._inflows.append(flow)
    
    def add_outflow(self, flow: Flow) -> None:
        """Add a flow that decreases this stock."""
        self._outflows.append(flow)
    
    def net_flow(self, time: float, state: dict[str, float]) -> float:
        """Calculate the net rate of change (inflows - outflows)."""
        inflows = sum(flow.rate(time, state) for flow in self._inflows)
        outflows = sum(flow.rate(time, state) for flow in self._outflows)
        return inflows - outflows
    
    @property
    def value(self) -> float:
        return self._current_value

    def set_value(self, value: float) -> None:
        self._current_value = value

    def reset(self) -> None:
        self._current_value = self.initial_value
    
    def __repr__(self) -> str:
        return f"Stock(name='{self.name}', value={self._current_value})"

