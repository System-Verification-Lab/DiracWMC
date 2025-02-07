""" Ising model generators, for example for things like square lattices """

import random
from typing import Literal
from ..models import IsingModel

def generate_square_lattice(size: int, weights: Literal["normal", "signed"] =
"normal") -> IsingModel:
    """ Generate a square lattice Ising model with random weights. The weights
        can be initialized using a normal distribution or a distribution picking
        from -1 and +1 with equal probability """
    model = IsingModel(size * size)
    weight_func = {
        "normal": (lambda: random.normalvariate(0, 1)),
        "signed": (lambda: random.choice((-1, 1))),
    }[weights]
    # Interaction strengths
    for i in range(size * size):
        if i + size < size * size:
            strength = weight_func()
            model[i, i + size] = strength
        if i % size != size - 1:
            strength = weight_func()
            model[i, i + 1] = strength
    # External field strengths
    for i in range(size * size):
        model[i] = random.normalvariate(0, 1)
    return model