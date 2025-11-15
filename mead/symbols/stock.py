from mead.symbols import Flow


class Stock:
    def __init__(self, name: str, initial_value: float = 0.0):
        self.name = name
        self.value = initial_value
        self.inflows: list[Flow] = []
        self.outflows: list[Flow] = []

    def add_inflow(self, *flows: Flow):
        for f in flows:
            self.inflows.append(f)

    def add_outflow(self, *flows: Flow):
        for f in flows:
            self.outflows.append(f)

    def update(self, dt: float):
        total_in = sum(f.compute() for f in self.inflows)
        total_out = sum(f.compute() for f in self.outflows)
        self.value += (total_in - total_out) * dt
        return self.value
