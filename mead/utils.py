from typing import Any, Sequence
from mead.core import Element, Constant


def as_element(value: Any) -> Element:
    match value:
        case float() | int():
            return Constant(f"literal_{value}", value)
        case Element():
            return value
        case _:
            raise ValueError(f"Can't handle type of {value}")


def deep_replace(obj, old, new, memo=None):
    if memo is None:
        memo = set()
    if id(obj) in memo:
        return obj

    memo.add(id(obj))

    if obj is old:
        return new

    if isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = deep_replace(item, old, new, memo)
        return obj

    if isinstance(obj, tuple):
        return tuple(deep_replace(x, old, new, memo) for x in obj)

    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = deep_replace(v, old, new, memo)
        return obj

    if hasattr(obj, "__dict__"):
        for attr, value in obj.__dict__.items():
            if attr == "model" and hasattr(value, "elements"):
                continue
            setattr(obj, attr, deep_replace(value, old, new, memo))
        return obj

    if hasattr(obj, "__slots__"):
        for slot in obj.__slots__:
            if hasattr(obj, slot):
                setattr(obj, slot, deep_replace(getattr(obj, slot), old, new, memo))
        return obj

    return obj
