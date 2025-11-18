import logging

logger = logging.getLogger(__name__)


class Historical:
    def __init__(self):
        self._history: list[float] = []

    def record(self, value: float):
        logger.info(f"{self} appending={value!r}")
        self._history.append(value)

    @property
    def last(self) -> float:
        if self._history:
            return self._history[-1]
        return 0.0

    @property
    def history(self):
        return self._history
