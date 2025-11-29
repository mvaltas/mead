from mead import Model, Element
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

        for new_elem in variants:
            name = new_elem.name
            if name not in new_model.elements:
                raise ValueError(f"Model has no element named {name}")

            old_elem = new_model.elements[name]
            deep_replace(new_model, old_elem, new_elem)
            new_model.elements[name] = new_elem
            new_elem.model = new_model

        return new_model

    def run_scenario(self, scenario: Scenario, duration: float):
        new_model = self._apply(scenario.variants)
        return new_model.run(duration=duration)

    def run_many(self, scenarios: list[Scenario], duration: float):
        results = {s.name: self.run_scenario(s, duration) for s in scenarios}
        return results

    def run(self, scenarios: Scenario | list[Scenario], duration: float):
        if isinstance(scenarios, list):
            return self.run_many(scenarios, duration)
        else:
            return self.run_many([scenarios], duration)
