from typing import Any
from mead.core import Element, Constant


def as_element(value: Any) -> Element:
    match value:
        case float() | int():
            return Constant(f"literal_{value}", value)
        case Element():
            return value
        case _:
            raise ValueError(f"Can't handle type of {value}")
