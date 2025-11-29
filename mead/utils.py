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


class DependencyMixin:
    """
    Provides a reusable implementation for the `dependencies` property.
    Subclasses should define a class-level attribute `_element_attrs` (Sequence[str])
    """

    _element_attrs: Sequence[str] = []  # To be overridden by subclasses

    @property
    def dependencies(self) -> list[Element]:
        deps: list[Element] = []
        for attr_name in self._element_attrs:
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, Element):
                deps.append(attr_value)
            elif isinstance(
                attr_value, list
            ):  # For elements like Min/Max that take a list of inputs
                for item in attr_value:
                    if isinstance(item, Element):
                        deps.append(item)
        return list(set(deps))


def deep_replace(obj, old, new):
    if obj is old:
        return new
    if isinstance(obj, list):
        return [deep_replace(x, old, new) for x in obj]
    if isinstance(obj, tuple):
        return tuple(deep_replace(x, old, new) for x in obj)
    if isinstance(obj, dict):
        return {k: deep_replace(v, old, new) for k, v in obj.items()}
    if hasattr(obj, "__dict__"):
        for attr, value in obj.__dict__.items():
            # Avoid infinite recursion, don't replace the model in an element
            if attr == "model" and hasattr(value, "elements"):
                continue
            setattr(obj, attr, deep_replace(value, old, new))
    return obj
