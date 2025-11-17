import logging

logger = logging.getLogger(__name__)


class Historical:
    def __init__(self):
        self.history: list[float] = []

    def record(self, value: float):
        logger.info(f"{self} appending={value!r}")
        self.history.append(value)

    def last(self) -> float:
        if self.history:
            return self.history[-1]
        return 0.0
