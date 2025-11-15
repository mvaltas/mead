from collections.abc import Callable

class Auxiliary:
    def __init__(self, name: str, formula: Callable[..., float]):
        self.name = name
        self.formula = formula

    def compute(self) -> float:
        return self.formula()
