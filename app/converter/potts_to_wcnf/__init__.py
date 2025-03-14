
from ...potts import PottsModel
from ...wcnf import WeightedCNFFormula
from itertools import product
import numpy as np

def potts_to_wncf(model: PottsModel, beta: float) -> WeightedCNFFormula:
    """ Convert a potts model to a weighted CNF formula, such that the partition
        function of the model is equal to the total weight of the formula """
    n, q = model.sites, model.states
    interactions = list(model.interactions())
    wcnf = WeightedCNFFormula(n * q + len(interactions))
    # For every interaction, add clause ((si and sj) <=> v)
    for index, (i, j, si, sj, _) in enumerate(interactions, n * q + 1):
        vi, vj = i * q + si + 1, j * q + sj + 1
        wcnf.formula.clauses += [[-vi, -vj, index], [vi, -index], [vj, -index]]
    # Add restriction that for any i, only one of the si can hold
    for i in range(n):
        wcnf.formula.clauses.append([i * q + si + 1 for si in range(q)])
        for si1, si2 in product(range(q), repeat=2):
            if si1 <= si2:
                continue
            index1, index2 = i * q + si1 + 1, i * q + si2 + 1
            wcnf.formula.clauses.append([-index1, -index2])
    # Weight of variables si is e^(-beta*external[i, si]) if si is 1 and 1 if si
    # is 0
    for i, si in product(range(n), range(q)):
        index = i * q + si + 1
        wcnf.weights[index] = np.exp(-beta * model[i, si])
        wcnf.weights[-index] = 1.0
    # Weight of connections is e^(-beta*strength) if connection is set and 1
    # otherwise
    for index, (_, _, _, _, strength) in enumerate(interactions, n * q + 1):
        wcnf.weights[index] = np.exp(-beta * strength)
        wcnf.weights[-index] = 1.0
    return wcnf
