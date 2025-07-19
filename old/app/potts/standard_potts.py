
from typing import Iterable, Any
import json
import jsonschema
import os
from itertools import product
import math

JSON_SCHEMA = json.loads(open(os.path.join(os.path.dirname(__file__),
"standard_schema.json"), "r").read())

class StandardPottsModel:
    """ Represents a q-state standard potts model with interaction strength J
        and a set of interactions between sites (each of which has a constant
        interaction strength). There is no external field """
    
    def __init__(self, sites: int, states: int, interaction_strength: float, *,
    interaction: Iterable[tuple[int, int]] | None = None):
        """ Constructor, given the number sites in the lattice, the number of
            states each lattice site can have, and the interaction strength.
            Additionally interaction pairs can be given """
        self._sites = sites
        self._states = states
        self._interaction_strength = interaction_strength
        self._interaction: set[tuple[int, int]] = (set() if interaction is None
        else set(interaction))

    def __len__(self) -> int:
        """ Returns the number of sites """
        return self._sites
    
    def __getitem__(self, key: tuple[int, int]) -> bool:
        """ Check if there is an interaction between two sites """
        return self.get_interaction(*key)
    
    def __setitem__(self, key: tuple[int, int], value: bool):
        """ Add/remove an interaction between two sites """
        return self.set_interaction(*key, value)

    def __repr__(self) -> str:
        """ Canonical representation """
        return (f"{self.__class__.__name__}({self._sites!r}, {self._states}, "
        f"{self._interaction_strength!r}, interaction={self._interaction!r})")
    
    def __str__(self) -> str:
        """ Convert this standard Potts model to JSON """
        return self.to_string()
    
    @classmethod
    def from_string(cls, text: str) -> "StandardPottsModel":
        """ Convert a JSON formatted string to a standard Potts model """
        data: dict[str, Any] = json.loads(text)
        jsonschema.validate(data, JSON_SCHEMA)
        model = cls(data["sites"], data["states"], data["interaction_strength"])
        for i, j in data["interaction"]:
            model.add_interaction(i, j)
        return model
    
    def to_string(self) -> str:
        """ Convert this standard Potts model to JSON """
        return json.dumps({
            "sites": self._sites,
            "states": self._states,
            "interaction_strength": self._interaction_strength,
            "interaction": list(self._interaction),
        })
    
    def get_interaction(self, i: int, j: int) -> bool:
        """ Check if there is an interaction between sites i and j """
        if i > j:
            i, j = j, i
        return (i, j) in self._interaction
    
    def set_interaction(self, i: int, j: int, present: bool):
        """ Add or remove an interaction, based on the present argument """
        if present:
            self.add_interaction(i, j)
        else:
            self.remove_interaction(i, j)

    def add_interaction(self, i: int, j: int):
        """ Add an interaction between sites. Has no effect if interaction is
            already present """
        if i > j:
            i, j = j, i
        self._interaction.add((i, j))

    def remove_interaction(self, i: int, j: int):
        """ Remove an interaction between sites. No no effect if interaction is
            not present """
        if i > j:
            i, j = j, i
        self._interaction.remove((i, j))

    def hamiltonian(self, config: Iterable[int]) -> float:
        """ get the hamiltonian function of a specific configuration of states,
            which needs to have the same length as this object """
        values = list(config)
        assert len(values) == self._sites
        total = 0.0
        for i, j in self._interaction:
            if config[i] == config[j]:
                total -= self._interaction_strength
        return total

    def partition_function(self, beta: float = 1.0) -> float:
        """ Get the partition function value with constant multiplier beta.
            NOTE: Uses brute force, so this function is slow """
        total = 0.0
        for config in product(range(self._states), repeat=self._sites):
            total += math.exp(-beta * self.hamiltonian(config))
        return total
    
    def interactions(self) -> Iterable[tuple[int, int]]:
        """ Get an iterator over all interactions in the model as tuple (i, j)
            """
        yield from self._interaction

    @property
    def interaction_strength(self) -> float:
        """ Get the interaction strength between sites """
        return self._interaction_strength

    @property
    def sites(self) -> int:
        """ Get the number of sites of this model """
        return self._sites
    
    @property
    def states(self) -> int:
        """ get the number of states every site in this model can have """
        return self._states
