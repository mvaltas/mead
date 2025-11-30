import itertools
from copy import replace
from collections import defaultdict
from typing import Iterable, Generator

from mead import Element, Scenario

InnerFactory = lambda: {}


class Experiment:

    def __init__(self, name: str):
        self.name = name
        self._variants: list[tuple] = []
        self._elements: dict[str, Element] = {}

    def add_variant(self, element: Element, /, **kwargs):
        self._elements[element.name] = element

        for attr, value in kwargs.items():
            var_list = (
                list(value)
                if (isinstance(value, Iterable) and not isinstance(value, str))
                else [value]
            )
            self._variants.append((element, element.name, attr, var_list))

    def scenarios(self) -> Generator[Scenario]:
        # [3] access to the tuple variants...
        all_value_variants = [v[3] for v in self._variants]

        for i, combinations in enumerate(itertools.product(*all_value_variants)):
            distinct_variants = []
            changes_by_element = defaultdict(dict)

            for j, value in enumerate(combinations):
                element_obj, _, attr_name, _ = self._variants[j]
                changes_by_element[element_obj][attr_name] = value

            for element, changes in changes_by_element.items():
                new_element = replace(element, **changes)
                distinct_variants.append(new_element)

            yield Scenario(f"{self.name}_{i}", variants=distinct_variants)

    def __str__(self):
        return "\n".join([f"{s}" for s in self.scenarios()])
