from typing import Callable


class Flow:
    """
    A Flow represents a rate that changes stocks over time.
    
    Flows can be inflows (increase stocks) or outflows (decrease stocks).
    Examples: birth rate, death rate, production rate, consumption rate.
    """
    
    def __init__(self, name: str, equation: Callable[[dict], float]):
        """
        Initialize a flow.
        
        Args:
            name: Unique identifier for the flow
            equation: Function that calculates the flow rate
                     Signature: (context: dict) -> float
                     where context contains time, state, and history lookup
        """
        self.name = name
        self._equation = equation
    
    def rate(self, context: dict) -> float:
        """
        Calculate the current rate of this flow.
        
        Args:
            context: Dictionary with time, state, and history lookup
            
        Returns:
            Flow rate at the current time
        """
        return self._equation(context)
    
    def __repr__(self) -> str:
        return f"Flow(name='{self.name}')"


# Helper functions for common flow patterns

def constant(value: float) -> Callable[[dict], float]:
    return lambda ctx: value

def delayed(source_stock: str, delay_time: float) -> Callable[[dict], float]:
    """
    Create a flow that returns a delayed value of a stock or other variable.

    Args:
        source_stock: Name of the source stock for this flow
        delay_time: Delay time for this flow to respond
    """
    def _delayed(ctx: dict) -> float:
        return ctx["history"](source_stock, delay_time)
    return _delayed


def fractional(stock_name: str, fraction: float) -> Callable[[dict], float]:
    """
    Create a flow proportional to a stock.
    
    Args:
        stock_name: Name of the stock to reference
        fraction: Fractional rate (e.g., 0.1 for 10% per time unit)
    """
    return lambda ctx: fraction * ctx["state"].get(stock_name, 0.0)


def table_lookup(stock_name: str, table: dict[float, float]) -> Callable[[dict], float]:
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

    return lambda ctx: interpolate(ctx["state"].get(stock_name, 0.0))


def step(height: float, step_time: float) -> Callable[[dict], float]:
    """Step function: 0 before step_time, height after."""
    return lambda ctx: height if ctx["time"] >= step_time else 0.0

def single_pulse(pulse: float, start: float, duration: float) -> Callable[[dict], float]:
    """Pulse function: height for duration width starting at start."""
    return lambda ctx: pulse if start <= ctx["time"] < start + duration else 0.0

def ramp(slope: float, start: float, end: float = float('inf')) -> Callable[[dict], float]:
    """Ramp function: increases linearly from start."""
    def _ramp(ctx):
        t = ctx["time"]
        if t < start:
            return 0.0
        elif t > end:
            return slope * (end - start)
        else:
            return slope * (t - start)
    return _ramp

# ============ SMOOTHING (Already have smoothed()) ============
def smoothed(stock_name: str, target_func: Callable, tau: float) -> Callable[[dict], float]:
    """
    Create a smoothed flow toward a target. Will goal seek
    the target in tau steps.

    Args:
        stock_name: Name of the stock holding the smoothed value
        target_func: Function that returns the target value
        tau: Time constant for smoothing
    """
    return lambda ctx: (target_func(ctx) - ctx["state"].get(stock_name, 0)) / tau

# ============ CONDITIONAL LOGIC ============
def clip(value_func: Callable, min_val: float, max_val: float):
    """Clamp value between min and max"""
    return lambda ctx: max(min_val, min(max_val, value_func(ctx)))

# ============ AGGREGATION ============
def sum_stocks(*stock_names: str):
    """Sum multiple stocks"""
    return lambda ctx: sum(ctx["state"].get(name, 0) for name in stock_names)

def min_stocks(*stock_names: str):
    """Minimum of multiple stocks"""
    return lambda ctx: min(ctx["state"].get(name, 0) for name in stock_names)

def max_stocks(*stock_names: str):
    """Maximum of multiple stocks"""
    return lambda ctx: max(ctx["state"].get(name, 0) for name in stock_names)

def stock_total(stock: str):
    return lambda ctx: ctx["state"].get(stock, 0)
