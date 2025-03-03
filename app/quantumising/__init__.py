
from typing import Iterable, Literal, Any
from functools import reduce
import numpy as np
from scipy.linalg import expm
import json
import jsonschema
import os

X_MATRIX = np.matrix([[0, 1], [1, 0]])
Z_MATRIX = np.matrix([[1, 0], [0, -1]])

JSON_SCHEMA = json.loads(open(os.path.join(os.path.dirname(
__file__), "schema.json"), "r").read())

class QuantumIsingModel:
    """ Quantum Ising model interaction and external field strengths in two
        directions (uniform over all spins) """
    
    def __init__(self, spin_count: int, *, interaction: dict[tuple[int, int],
    float] | None = None, external_field_x: float = 0.0, external_field_z:
    float = 0.0):
        """ Constructor """
        self._spin_count = spin_count
        # Interaction strengths
        self._interaction = {} if interaction is None else interaction.copy()
        # External field strength in both directions
        self.external_field_x = external_field_x
        self.external_field_z = external_field_z

    def __len__(self) -> int:
        """ Returns the number of spins """
        return self._spin_count

    def __getitem__(self, key: tuple[int, int]) -> float:
        """ Get either the interaction strength between two spins """
        return self.get_interaction(*key)
    
    def __setitem__(self, key: tuple[int, int], value: float):
        """ Set the interaction strength between two spins spin(s). Overrides
            any existing strength """
        self.set_interaction(*key, value)

    def __str__(self) -> str:
        """ Convert this Ising model to JSON """
        return self.to_string()

    def __repr__(self) -> str:
        """ Canonical representation """
        return (f"{self.__class__.__name__}({self._spin_count!r}, interaction="
        f"{self._interaction!r}, external_field_x={self.external_field_x!r}, "
        f"external_field_z={self.external_field_z!r})")

    @classmethod
    def from_string(cls, text: str) -> "QuantumIsingModel":
        """ Convert JSON to an IsingModel object """
        data: dict[str, Any] = json.loads(text)
        jsonschema.validate(data, JSON_SCHEMA)
        model = cls(data["spin_count"])
        for i, j, strength in data["interaction"]:
            model.set_interaction(i, j, strength)
        model.external_field_x = float(data.get("external_field_x", 0.0))
        model.external_field_z = float(data.get("external_field_z", 0.0))
        return model

    def to_string(self) -> str:
        """ Convert this Ising model to JSON """
        return json.dumps({
            "nodes": self._spin_count,
            "external_field_x": self.external_field_x,
            "external_field_z": self.external_field_z,
            "interactions": [(i, j, strength) for (i, j), strength in
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

    def partition_function(self, beta: float) -> float:
        """ Returns the approximate partition function of the model, using
            matrix exponentiation, given the inverse temperature beta. This
            method is very slow for large models """
        # Partition function is Tr(e^(-beta*H))
        return expm(-beta * self.hamiltonian()).trace()

    def hamiltonian(self) -> np.matrix:
        """ Determine the Hamiltonian matrix of this model. This method is very
            slow for large models """
        return np.matrix(self._interaction_hamiltonian() +
        self._external_field_hamiltonian("x") +
        self._external_field_hamiltonian("z"))
    
    def interactions(self) -> Iterable[tuple[int, int, float]]:
        """ Get an iterator over all interactions in the model as tuples (i, j,
            strength) """
        for (i, j), strength in self._interaction.items():
            yield (i, j, strength)

    def _interaction_hamiltonian(self) -> np.matrix:
        """ Get the interaction part of the Hamiltonian of this model """
        current = np.zeros((2 ** self._spin_count, 2 ** self._spin_count))
        # Lattice interactions
        for (i, j), strength in self._interaction.items():
            current += strength * reduce(np.kron, [
                np.identity(2 ** i),
                Z_MATRIX,
                np.identity(2 ** (j - i - 1)),
                Z_MATRIX,
                np.identity(2 ** (self._spin_count - j - 1))
            ])
        return np.matrix(current)
    
    def _external_field_hamiltonian(self, direction: Literal["x", "z"]) -> (
    np.matrix):
        """ Get the external field Hamiltonian of one of the two directions """
        sub_matrix = X_MATRIX if direction == "x" else Z_MATRIX
        field_strength = (self.external_field_x if direction == "x" else
        self.external_field_z)
        current = np.zeros((2 ** self._spin_count, 2 **
        self._spin_count))
        for i in range(self._spin_count):
            current += field_strength * reduce(np.kron, [
                np.identity(2 ** i),
                sub_matrix,
                np.identity(2 ** (self._spin_count - i - 1))
            ])
        return np.matrix(current)
