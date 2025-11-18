from mead.symbols import BaseSymbol, Stock


class Flow(BaseSymbol):
    pass

class GoalFlow(Flow):

    def __init__(
            self, 
            name: str, 
            stock: Stock, 
            goal: BaseSymbol, 
            max_rate: float | None = None):
        self.stock = stock
        self.goal = goal
        self.max_rate = max_rate
        super().__init__(name, formula=self._goal_seeking_formula)

    def _goal_seeking_formula(self) -> float:
        diff = float(self.goal) - float(self.stock.value)
        if self.max_rate is not None:
            # Clamp to max_rate in either direction
            diff = max(-self.max_rate, min(self.max_rate, diff))
        return diff


