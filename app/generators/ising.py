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

def generate_random_graph(size: int, avg_degree: float = 3.0, weights: Literal[
"normal", "signed"] = "normal"):
    """ Generate a random graph Ising model with a certain average degree. The
        weights can be initialized using a normal distribution or a distribution
        picking from -1 and +1 with equal probability """
    model = IsingModel(size)
    weight_func = {
        "normal": (lambda: random.normalvariate(0, 1)),
        "signed": (lambda: random.choice((-1, 1))),
    }[weights]
    edge_count = round(size * avg_degree / 2.0)
    found: set[tuple[int, int]] = set()
    # Interaction strengths
    for _ in range(edge_count):
        valid = False
        edge = (0, 0)
        while not valid:
            edge = (random.randrange(size), random.randrange(size))
            if edge[0] > edge[1]:
                edge = (edge[1], edge[0])
            if edge[0] == edge[1] or edge in found:
                continue
            found.add(edge)
            valid = True
        strength = weight_func()
        model[edge] = strength
    # External field strengths
    for i in range(size):
        model[i] = random.normalvariate(0, 1)
    return model