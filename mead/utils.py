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


class DependenciesProperty:
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
                deps.extend(attr_value.dependencies)
            elif isinstance(
                attr_value, list
            ):  # For elements like Min/Max that take a list of inputs
                for item in attr_value:
                    if isinstance(item, Element):
                        deps.append(item)
                        deps.extend(item.dependencies)
        return list(set(deps))

