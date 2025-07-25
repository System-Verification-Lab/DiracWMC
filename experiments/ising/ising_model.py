
from __future__ import annotations
from typing import Iterable, Literal
from itertools import product
import os
import json
import jsonschema
import math

JSON_SCHEMA = json.loads(open(os.path.join(os.path.dirname(__file__),
"schema.json"), "r").read())

class IsingModel:
    """ Classical Ising model with interaction and external field strengths """

    def __init__(self, spin_count: int, *, interaction: dict[tuple[int, int],
    float] | None = None, external_field: Iterable[float] | None = None):
        """ Constructor with number of spins. Optionally interactions and
            external field strengths can be given """
        self._spin_count = spin_count
        # Interaction strengths
        if interaction is None:
            self._interaction = {}
        else:
            self._interaction = interaction.copy()
        # External field strength per node
        if external_field is None:
            self._external_field = [0.0] * spin_count
        else:
            self._external_field = list(external_field)

    def __len__(self) -> int:
        """ Returns the number of spins """
        return self._spin_count

    def __getitem__(self, key: int | tuple[int, int]) -> float:
        """ Get either the external field strength or interaction strength at
            specific spin(s), depending on the key """
        if isinstance(key, int):
            return self.get_external_field(key)
        return self.get_interaction(*key)
    
    def __setitem__(self, key: int | tuple[int, int], value: float):
        """ Set the external field strength or interaction strength at specific
            spin(s), depending on the key. Overrides any existing strength """
        if isinstance(key, int):
            self.set_external_field(key, value)
        else:
            self.set_interaction(*key, value)

    def __repr__(self):
        """ Canonical representation """
        return (f"{self.__class__.__name__}({self._spin_count!r}, interaction="
        f"{self._interaction!r}, external_field={self._external_field!r})")

    def __str__(self) -> str:
        """ Convert this Ising model to JSON """
        return self.to_string()

    @classmethod
    def from_string(cls, text: str) -> IsingModel:
        """ Convert JSON to an IsingModel object """
        data = json.loads(text)
        jsonschema.validate(data, JSON_SCHEMA)
        model = cls(data["spin_count"])
        for i, j, strength in data["interaction"]:
            model.set_interaction(i, j, strength)
        model._external_field = list(map(float, data["external_field"]))
        return model

    def to_string(self) -> str:
        """ Convert this Ising model to JSON """
        return json.dumps({
            "spin_count": self._spin_count,
            "external_field": self._external_field,
            "interaction": [(i, j, strength) for (i, j), strength in
            self._interaction.items()]
        })

    def get_interaction(self, i: int, j: int) -> float:
        """ Get the interaction strength between two spins """
        if i > j:
            i, j = j, i
        return self._interaction.get((i, j), 0.0)
    
    def set_interaction(self, i: int, j: int, strength: float, *,
    add_to_existing: bool = False):
        """ Set the interaction strength between two spins. If add_to_existing
            is set to true, the strength will be summed with any existing
            strength """
        if i > j:
            i, j = j, i
        existing = 0.0
        if add_to_existing:
            existing = self._interaction.get((i, j), 0.0)
        self._interaction[i, j] = existing + strength

    def get_external_field(self, i: int) -> float:
        """ Get the external field strength at the given spin index """
        return self._external_field[i]
    
    def set_external_field(self, i: int, strength: float, *, add_to_existing:
    bool = False):
        """ Set the external field strength at a spin index i. If
            add_to_existing is set to true, the strength will be summed with any
            existing strength """
        existing = 0.0
        if add_to_existing:
            existing = self._external_field[i]
        self._external_field[i] = existing + strength

    def hamiltonian(self, config: Iterable[Literal[-1, 1]]) -> float:
        """ Get the hamiltonian function of a specific configuration, which
            needs to have the same length as this object """
        values = list(config)
        assert len(values) == self._spin_count
        total = 0.0
        total -= sum(values[i] * values[j] * s for (i, j), s in
        self._interaction.items())
        total -= sum(v * s for v, s in zip(values, self._external_field))
        return total

    def partition_function(self, beta: float = 1.0) -> float:
        """ Get the partition function value at inverse temperature beta """
        total = 0.0
        for config in product((-1, 1), repeat=self._spin_count):
            total += math.exp(-beta * self.hamiltonian(config))
        return total

    @property
    def external_field(self) -> list[float]:
        """ Access external field strengths """
        return self._external_field

    def interactions(self) -> Iterable[tuple[int, int, float]]:
        """ Get an iterator over all interactions in the model as tuples (i, j,
            strength) """
        for (i, j), strength in self._interaction.items():
            yield (i, j, strength)