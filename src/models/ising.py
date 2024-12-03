
from typing import Iterable
import numpy as np
from itertools import product
import json
import jsonschema

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "nodes": {"type": "integer"},
        "external_field": {
            "type": "array",
            "items": {"type": "number"},
        },
        "interactions": {
            "type": "array",
            "items": {
                "type": "array",
                "items": False,
                "prefixItems": [
                    {"type": "integer"},
                    {"type": "integer"},
                    {"type": "number"},
                ]
            },
        },
    },
}

class IsingModel:
    """ Classical Ising model, interactions between nodes and an external field
        acting on each node individually """
    
    def __init__(self, node_count: int):
        """ Constructor, given the number of nodes in the model """
        self._node_count = node_count
        self._interactions: dict[tuple[int, int], float] = {}
        self._external_field = [0.0] * node_count
    
    @classmethod
    def from_string(self, text: str):
        """ Convert a JSON-formatted string to an Ising Model object """
        data = json.loads(text)
        jsonschema.validate(data, JSON_SCHEMA)
        model = IsingModel(data["nodes"])
        for i, j, strength in data["interactions"]:
            model._interactions[i, j] = strength
        model._external_field = list(map(float, data["external_field"]))
        return model

    def to_string(self) -> str:
        """ Convert an Ising Model object to a JSON-formatted string, that can
            be converted back later """
        return json.dumps({
            "nodes": self._node_count,
            "external_field": self._external_field,
            "interactions": [(i, j, strength) for (i, j), strength in
            self._interactions.items()]
        })

    def partition_function(self, beta: float) -> float:
        """ Determine the parition function of the Ising model at the given
            inverse temperature """
        return sum(np.exp(-beta * self.hamiltonian(config)) for config in
        product([-1, 1], repeat=self._node_count))

    def hamiltonian(self, config: Iterable[int]) -> float:
        """ Get the Hamiltonian of the model evaluated for a given configuration
            """
        total = 0.0
        for (i, j), strength in self._interactions.items():
            total -= strength * config[i] * config[j]
        for spin, strength in zip(config, self._external_field):
            total -= strength * spin
        return total
    
    @property
    def external_field(self) -> list[float]:
        """ Get the external field of the Ising Model, which can be modified """
        return self._external_field
    
    def add_interaction(self, i: int, j: int, strength: float, *,
    add_to_existing: bool = False):
        """ Add an interaction between two nodes i and j with the given
            strength. If add_to_existing is True, no error will be thrown when
            the interactions already exists, and the interaction strength will
            be added to the current strength """
        if not add_to_existing and (i, j) in self._interactions:
            raise RuntimeError(f"Interaction between {i} and {j} already "
            "exists")
        self._interactions.setdefault((i, j), 0.0)
        self._interactions[i, j] += strength

    def __str__(self) -> str:
        """ Get the string representation of the model as a JSON-formatted
            string """
        return self.to_string()
    
    def __len__(self) -> int:
        """ Number of nodes in the model """
        return self._node_count
