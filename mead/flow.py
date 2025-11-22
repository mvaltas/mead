from typing import Callable


class Flow:
    """
    A Flow represents a rate that changes stocks over time.
    
    Flows can be inflows (increase stocks) or outflows (decrease stocks).
    Examples: birth rate, death rate, production rate, consumption rate.
    """
    
    def __init__(self, name: str, equation: Callable[[float, dict[str, float]], float]):
        """
        Initialize a flow.
        
        Args:
            name: Unique identifier for the flow
            equation: Function that calculates the flow rate
                     Signature: (time: float, state: dict[str, float]) -> float
                     where state maps stock names to their current values
        """
        self.name = name
        self._equation = equation
    
    def rate(self, time: float, state: dict[str, float]) -> float:
        """
        Calculate the current rate of this flow.
        
        Args:
            time: Current simulation time
            state: Dictionary mapping stock names to current values
            
        Returns:
            Flow rate at the current time
        """
        return self._equation(time, state)
    
    def __repr__(self) -> str:
        return f"Flow(name='{self.name}')"


# Helper functions for common flow patterns

def constant(value: float) -> Callable[[float, dict[str, float]], float]:
    return lambda t, s: value


def fractional(stock_name: str, fraction: float) -> Callable[[float, dict[str, float]], float]:
    """
    Create a flow proportional to a stock.
    
    Args:
        stock_name: Name of the stock to reference
        fraction: Fractional rate (e.g., 0.1 for 10% per time unit)
    """
    return lambda t, s: fraction * s.get(stock_name, 0.0)


def table_lookup(stock_name: str, table: dict[float, float]) -> Callable[[float, dict[str, float]], float]:
    """Create a flow based on linear interpolation from a lookup table."""
    keys = sorted(table.keys())

    def interpolate(value: float) -> float:
        if value <= keys[0]:
            return table[keys[0]]
        if value >= keys[-1]:
            return table[keys[-1]]

        for i in range(len(keys) - 1):
            if keys[i] <= value <= keys[i + 1]:
                x0, x1 = keys[i], keys[i + 1]
                y0, y1 = table[x0], table[x1]
                return y0 + (y1 - y0) * (value - x0) / (x1 - x0)
        return 0.0

    return lambda t, s: interpolate(s.get(stock_name, 0.0))


def step(height: float, step_time: float) -> Callable[[float, dict], float]:
    """Step function: 0 before step_time, height after."""
    return lambda t, s: height if t >= step_time else 0.0

def pulse(height: float, start: float, width: float) -> Callable[[float, dict], float]:
    """Pulse function: height for duration width starting at start."""
    return lambda t, s: height if start <= t < start + width else 0.0

def ramp(slope: float, start: float, end: float = float('inf')) -> Callable[[float, dict], float]:
    """Ramp function: increases linearly from start."""
    def _ramp(t, s):
        if t < start:
            return 0.0
        elif t > end:
            return slope * (end - start)
        else:
            return slope * (t - start)
    return _ramp

# ============ SMOOTHING (Already have smoothed()) ============
def smoothed(stock_name: str, target_func: Callable, tau: float,
            state_key: str = "smoothed") -> Callable[[float, dict[str, float]], float]:
    """
    Create a smoothed flow toward a target.

    Args:
        stock_name: Name of the stock holding the smoothed value
        target_func: Function that returns the target value
        tau: Time constant for smoothing
        state_key: Key in state dict for current smoothed value
    """
    return lambda t, s: (target_func(t, s) - s.get(stock_name, 0)) / tau

def smooth(stock_name: str, input_value: Callable, tau: float):
    """First-order exponential smooth - alias for smoothed()"""
    return smoothed(stock_name, input_value, tau)

# ============ GOAL-SEEKING ============
def goal_gap(stock_name: str, target: float, adjustment_time: float):
    """Goal-seeking flow: (target - current) / adjustment_time"""
    return lambda t, s: (target - s.get(stock_name, 0)) / adjustment_time

def goal_gap_dynamic(stock_name: str, target_func: Callable, adjustment_time: float):
    """Goal-seeking with dynamic target"""
    return lambda t, s: (target_func(t, s) - s.get(stock_name, 0)) / adjustment_time

# ============ CONDITIONAL LOGIC ============
def if_then_else(condition: Callable, true_val: Callable, false_val: Callable):
    """Conditional flow"""
    return lambda t, s: true_val(t, s) if condition(t, s) else false_val(t, s)
def clip(value_func: Callable, min_val: float, max_val: float):
    """Clamp value between min and max"""
    return lambda t, s: max(min_val, min(max_val, value_func(t, s)))
# ============ AGGREGATION ============
def sum_stocks(*stock_names: str):
    """Sum multiple stocks"""
    return lambda t, s: sum(s.get(name, 0) for name in stock_names)
def min_stocks(*stock_names: str):
    """Minimum of multiple stocks"""
    return lambda t, s: min(s.get(name, 0) for name in stock_names)
def max_stocks(*stock_names: str):
    """Maximum of multiple stocks"""
    return lambda t, s: max(s.get(name, 0) for name in stock_names)
