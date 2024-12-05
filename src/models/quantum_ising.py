
from scipy.linalg import expm
import numpy as np
from functools import reduce
import json
import jsonschema

X_MATRIX = np.matrix([[0, 1], [1, 0]])
Z_MATRIX = np.matrix([[1, 0], [0, -1]])

JSON_SCHEMA = {
    "type": "object",
    "required": ["nodes", "interactions"],
    "additionalProperties": False,
    "properties": {
        "nodes": {"type": "integer"},
        "external_factor": {"type": "number"},
        "interactions": {
            "type": "array",
            "items": {
                "type": "array",
                "items": False,
                "prefixItems": [
                    {"type": "integer"},
                    {"type": "integer"},
                    {"type": "number"},
                ],
            },
        },
    },
}

class QuantumIsingModel:
    """ Quantum Ising model, using Hamiltonian
        H = -sum[i,j in R^d]{J_ij*sigma_i^z*sigma_j^z}-Gamma*sum[j]{sigma_j^x}
        """
    
    def __init__(self, node_count: int, external_factor: float = 0.0):
        """ Constructor, given the number of nodes in the lattice, and external
            field strength """
        self._node_count = node_count
        self._external_factor = external_factor
        self._interactions: dict[tuple[int, int], float] = {}

    @classmethod
    def from_string(cls, text: str) -> "QuantumIsingModel":
        """ Parse a JSON-formatted string and get the corresponding Quantum
            Ising Model """
        data = json.loads(text)
        jsonschema.validate(data, JSON_SCHEMA)
        external_factor = data.get("external_factor", 0.0)
        model = cls(data["nodes"], external_factor)
        for i, j, strength in data["interactions"]:
            model.add_interaction(i, j, strength)
        return model

    def to_string(self) -> str:
        """ Convert the Quantum Ising Model to a JSON-formatted string, that can
            also be converted back to a QuantumIsingModel object """
        return json.dumps({
            "nodes": self._node_count,
            "external_factor": self._external_factor,
            "interactions": [(i, j, strength) for (i, j), strength in
            self._interactions.items()]
        })

    def add_interaction(self, i: int, j: int, strength: float, add_to_existing:
    bool = False):
        """ Add an interaction between two nodes i and j with a given strength.
            If add_to_existing is set to True, this will not throw an error when
            an interaction between the nodes already exists, and instead will
            add the strength to the existing strength """
        if i > j: i, j = j, i
        assert i != j
        if not add_to_existing and (i, j) in self._interactions:
            raise RuntimeError(f"Interaction between {i} and {j} already "
            "exists")
        self._interactions.setdefault((i, j), 0.0)
        self._interactions[i, j] += strength

    def partition_function(self, beta: float) -> float:
        """ Returns the approximate partition function of the model, using
            matrix exponentiation, given the inverse temperature beta. This
            method is very slow for large models """
        # Partition function is Tr(e^(-beta*H))
        return expm(-beta * self.hamiltonian()).trace()

    def hamiltonian(self) -> np.matrix:
        """ Determine the Hamiltonian matrix of this model. This method is very
            slow for large models """
        current = np.zeros((2 ** self._node_count, 2 ** self._node_count))
        # Lattice interactions
        for (i, j), strength in self._interactions.items():
            current += strength * reduce(np.kron, [
                np.identity(2 ** i),
                Z_MATRIX,
                np.identity(2 ** (j - i - 1)),
                Z_MATRIX,
                np.identity(2 ** (self._node_count - j - 1))
            ])
        # External field
        current += self._external_factor * reduce(np.kron, (X_MATRIX for _ in
        range(self._node_count)))
        return np.matrix(current)

    @property
    def external_factor(self) -> float:
        """ Get the external factor gamma of the model """
        return self._external_factor

    @property
    def node_count(self) -> int:
        """ Get the number of nodes in the model """
        return self._node_count
    
    @property
    def interactions(self) -> dict[tuple[int, int], float]:
        """ Get the interactions in the model. This should not be modified
            without copying """
        return self._interactions

    def __str__(self) -> str:
        """ Convert to string using the same format that from_string() uses """
        return self.to_string()
    
    def __len__(self) -> int:
        """ Get the number of nodes in the model """
        return self._node_count