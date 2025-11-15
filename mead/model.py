from mead.symbols import Stock, Flow, Auxiliary


class Model:
    def __init__(self):
        self.stocks = {}
        self.flows = {}
        self.aux = {}
        self.time = 0

    def add_stock(self, stock: Stock):
        self.stocks[stock.name] = stock

    def add_flow(self, flow: Flow):
        self.flows[flow.name] = flow

    def add_auxiliary(self, aux: Auxiliary):
        self.aux[aux.name] = aux

    def step(self, dt=1.0):
        # Update all flows first (they may depend on auxiliaries)
        for f in self.flows.values():
            f.compute()

        # Update all stocks
        for s in self.stocks.values():
            s.update(dt)

        self.time += dt

    def run(self, steps, dt=1.0):
        history = {name: [] for name in self.stocks}
        for _ in range(steps):
            self.step(dt)
            for name, stock in self.stocks.items():
                history[name].append(stock.value)
        return history
