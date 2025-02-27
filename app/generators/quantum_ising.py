""" Quantum Ising model generators """

import random
from typing import Literal
from ..models import QuantumIsingModel

def generate_ring(size: int, weights: Literal["normal", "signed"] = "normal", *,
line: bool = False) -> QuantumIsingModel:
    """ Generate a ring quantum Ising model with random weights. The weights
        can be initialized using a normal distribution or a distribution picking
        from -1 and +1 with equal probability """
    model = QuantumIsingModel(size)
    weight_func = {
        "normal": (lambda: random.normalvariate(0, 1)),
        "signed": (lambda: random.choice((-1, 1))),
    }[weights]
    for i in range(size - 1 if line else size):
        strength = weight_func()
        model[i, (i + 1) % size] = strength
    model.external_field_x = random.normalvariate()
    return model