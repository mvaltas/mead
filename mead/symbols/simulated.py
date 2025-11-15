class Simulated:

    name: str | None = None

    def timestep(self, step: int) -> None:
        raise Exception("not implemented")

    def commit(self) -> None:
        raise Exception("not implemented")

    def __hash__(self) -> int:
        return hash(self.name)
