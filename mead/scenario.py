from typing import Iterable
from mead import Model, Element, Stock
from mead.model import IntegrationMethod
from dataclasses import dataclass
from copy import deepcopy
from mead.utils import deep_replace


@dataclass
class Scenario:
    name: str
    variants: list[Element]


class ScenarioRunner:
    def __init__(self, base_model: Model):
        self.base_model = base_model

    def _apply(self, variants: list[Element]) -> Model:
        new_model = deepcopy(self.base_model)

        replacements = {v.name: v for v in variants}

        for name, new_elem in replacements.items():
            if name in new_model.elements:
                new_model.elements[name] = new_elem
                if isinstance(new_elem, Stock):
                    new_model.stocks[name] = new_elem
            # elements contain a reference of the model itself
            new_elem.model = new_model

        deep_replace(new_model, replacements)

        return new_model

    def run_scenario(
        self, scenario: Scenario, duration: float, method: IntegrationMethod = "euler"
    ):
        new_model = self._apply(scenario.variants)
        return new_model.run(duration=duration, method=method)

    def run_many(
        self,
        scenarios: Iterable[Scenario],
        duration: float,
        method: IntegrationMethod = "euler",
    ):
        results = {s.name: self.run_scenario(s, duration, method) for s in scenarios}
        return results

    def run(
        self,
        scenarios: Scenario | Iterable[Scenario],
        duration: float,
        method: IntegrationMethod = "euler",
    ):
        if isinstance(scenarios, Iterable):
            return self.run_many(scenarios, duration, method)
        else:
            return self.run_many([scenarios], duration, method)
