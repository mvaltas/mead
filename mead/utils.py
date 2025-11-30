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


def deep_replace(
    obj: Any, replacements: dict[str, Element], memo: set | None = None
) -> Any:
    if memo is None:
        memo = set()

    # avoid infinite recursion on circular references
    if id(obj) in memo:
        return obj
    memo.add(id(obj))

    if isinstance(obj, Element) and obj.name in replacements:
        return replacements[obj.name]

    if isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = deep_replace(item, replacements, memo)
    elif isinstance(obj, tuple):
        # Tuples are immutable we need to create a new one
        return tuple(deep_replace(x, replacements, memo) for x in obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = deep_replace(v, replacements, memo)
    elif hasattr(obj, "__dict__"):
        for attr, value in obj.__dict__.items():
            # Avoid recursing into the entire model from an element
            if attr == "model":
                continue
            setattr(obj, attr, deep_replace(value, replacements, memo))
    return obj
