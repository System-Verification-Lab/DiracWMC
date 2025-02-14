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

def generate_random_graph(size: int, degree: int = 3, weights: Literal["normal",
"signed"] = "normal"):
    """ Generate a random regular graph with vertices with the given degree. The
        interaction weights are generated according to the distribution given
        (by default normal(0, 1), but a sample from +-1 is also possible).
        External field strengths are set independently per vertex to a value
        sampled from normal(0, 1). Throws an error if size*degree is not even
        """
    model = IsingModel(size)
    weight_func = {
        "normal": lambda: random.normalvariate(0, 1),
        "signed": lambda: random.choice((-1, 1)),
    }[weights]
    assert size * degree % 2 == 0
    nodes = sum(([i] * degree for i in range(size)), [])
    random.shuffle(nodes)
    for i, j in zip(nodes[::2], nodes[1::2]):
        model[i, j] = weight_func()
    # External field strengths
    for i in range(size):
        model[i] = random.normalvariate(0, 1)
    return model