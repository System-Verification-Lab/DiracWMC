
from typing import Any, Iterable
import json
import os
import jsonschema
from itertools import product
import math

JSON_SCHEMA = json.loads(open(os.path.join(os.path.dirname(__file__),
"schema.json"), "r").read())

class PottsModel:
    """ Represents a q-state generalized Potts model with a function J(i, j, si,
        sj) of connection strengths and a function h(i, si) of external field
        strengths. Note that the states are numbered 0,...,q-1 and the sites are
        numbered 0,...,n-1 """
    
    def __init__(self, sites: int, states: int, *, interaction: dict[tuple[int,
    int, int, int], float] | None = None, external_field: dict[tuple[int, int],
    float] | None = None):
        """ Constructor, given the number of sites and functions indicating
            interaction strengths and external field strengths. The interaction
            strengths map from (i, j, si, sj) and the external field strnegths
            from (i, si) """
        self._sites = sites
        self._states = states
        self._interaction = {} if interaction is None else interaction.copy()
        self._external_field = ({} if external_field is None else
        external_field.copy())

    def __len__(self) -> int:
        """ Returns the number of sites """
        return self._sites
    
    def __getitem__(self, key: tuple[int, int] | tuple[int, int, int, int]) -> (
    float):
        """ Get either the external field strength or interaction strength at
            specific site(s), depending on the key """
        if len(key) == 2:
            return self.get_external_field(*key)
        return self.get_interaction(*key)

    def __setitem__(self, key: tuple[int, int] | tuple[int, int, int, int],
    value: float) -> float:
        """ Set the external field strength or interaction strength at given
            site(s), depending on the key. Overrides any existing strength """
        if len(key) == 2:
            self.set_external_field(*key, value)
        else:
            self.set_external_field(*key, value)

    def __repr__(self):
        """ Canonical representation """
        return (f"{self.__class__.__name__}({self._sites!r}, interaction="
        f"{self._interaction!r}, external_field={self._external_field!r})")

    def __str__(self) -> str:
        """ Convert this Potts model to JSON """
        return self.to_string()

    @classmethod
    def from_string(cls, text: str) -> "PottsModel":
        """ Convert a JSON formatted string to a Potts model """
        data: dict[str, Any] = json.loads(text)
        jsonschema.validate(data, JSON_SCHEMA)
        model = cls(data["sites"], data["states"])
        for inter in data["interaction"]:
            model.set_interaction(*inter)
        for ext in data["external_field"]:
            model.set_external_field(*ext)
        return model

    def to_string(self) -> str:
        """ Convert this Potts model to JSON """
        return json.dumps({
            "sites": self._sites,
            "states": self._states,
            "external_field": [(*k, v) for k, v in
            self._external_field.items()],
            "interaction": [(*k, v) for k, v in self._interaction.items()],
        })
    
    def get_interaction(self, i: int, j: int, si: int, sj: int) -> float:
        """ Get the interaction strength between two sites given their states
            """
        if i > j:
            i, j = j, i
            si, sj = sj, si
        return self._interaction.get((i, j, si, sj), 0.0)

    def set_interaction(self, i: int, j: int, si: int, sj: int, strength: float,
    *, add_to_existing: bool = False) -> float:
        """ Set the interaction strength between two sites given their states.
            If add_to_existing is set to true, the strength will be summed with
            the existing strength """
        if i > j:
            i, j = j, i
            si, sj = sj, si
        existing = 0.0
        if add_to_existing:
            existing = self._interaction.get((i, j, si, sj), 0.0)
        self._interaction[i, j, si, sj] = existing + strength

    def get_external_field(self, i: int, si: int) -> float:
        """ Get the external field strength at site i when in state si """
        return self._external_field.get((i, si), 0.0)
    
    def set_external_field(self, i: int, si: int, strength: float, *,
    add_to_existing: bool = False):
        """ Set the external field strength at the given site given the state.
            If add_to_existing is set to true, the strength will be added to the
            existing strength """
        existing = 0.0
        if add_to_existing:
            existing = self._external_field.get((i, si), 0.0)
        self._external_field[i, si] = existing + strength

    def hamiltonian(self, config: Iterable[int]) -> float:
        """ Get the hamiltonian function of a specific configuration of states,
            which needs to have the same length as this object """
        values = list(config)
        assert len(values) == self._sites
        total = 0.0
        for i, j in product(range(self._sites), repeat=2):
            total += self._interaction.get((i, j, config[i], config[j]), 0.0)
        for i in range(self._sites):
            total += self._external_field.get((i, config[i]), 0.0)
        return total

    def partition_function(self, beta: float = 1.0) -> float:
        """ Get the partition function value with constant multiplier beta.
            NOTE: Uses brute force, so this function is slow """
        total = 0.0
        for config in product(range(self._states), repeat=self._sites):
            total += math.exp(-beta * self.hamiltonian(config))
        return total

    def external_field(self) -> Iterable[tuple[int, int, float]]:
        """ Get an iterator over all external field strengths in the model as
            tuples (i, si, strength) """
        yield from ((*k, v) for k, v in self._external_field.items())

    def interactions(self) -> Iterable[tuple[int, int, int, int, float]]:
        """ Get an iterator over all interaction strengths in the model as (i,
            j, si, sj, strength) """
        yield from ((*k, v) for k, v in self._interaction.items())

    @property
    def sites(self) -> int:
        """ Get the number of sites of this model """
        return self._sites
    
    @property
    def states(self) -> int:
        """ Get the number of states every site in this model can have """
        return self._states