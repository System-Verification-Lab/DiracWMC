
from typing import Iterable
import numpy as np
from itertools import product

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
        ...

    def to_string(self) -> str:
        ...

    def partition_function(self, beta: float) -> float:
        """ Determine the parition function of the Ising model at the given
            inverse temperature """
        return sum(np.exp(-beta * self.hamiltonian(config)) for config in
        product([-1, 1], repeat=self._node_count))

    def hamiltonian(self, config: Iterable[int]):
        """ Get the Hamiltonian of the model evaluated for a given configuration
            """
        ...
