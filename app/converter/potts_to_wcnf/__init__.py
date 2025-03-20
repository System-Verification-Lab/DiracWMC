
from ...potts import PottsModel, StandardPottsModel
from ...wcnf import WeightedCNFFormula
from itertools import product
import numpy as np

def potts_to_wcnf(model: PottsModel, beta: float) -> WeightedCNFFormula:
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

def standard_potts_to_potts(model: StandardPottsModel) -> PottsModel:
    """ Convert a standard potts model object to a potts model object, that
        still represents the same model """
    interaction: dict[tuple[int, int, int, int], float] = {}
    for i, j in model.interactions():
        for s in range(model.states):
            interaction[i, j, s, s] = -model.interaction_strength
    return PottsModel(model.sites, model.states, interaction=interaction)

def standard_potts_to_wcnf(model: StandardPottsModel, beta: float) -> (
WeightedCNFFormula):
    """ Convert a standard potts model to a weighted CNF formula, such that the
        partition function of the model is equal to the total weight of the
        formula """
    n, q = model.sites, model.states
    k = len(bin(q - 1)[2:])
    interactions = list(model.interactions())
    strength = model.interaction_strength
    wcnf = WeightedCNFFormula(n * k + len(interactions) * k)
    # For every interactions, add clause all(x <=> y) <=> a
    for index, (i, j) in enumerate(interactions):
        start_index = n * k + 1 + index * k
        start_i, start_j = k * i + 1, k * j + 1
        wcnf.formula.clauses += [
            [start_index, start_i, start_j],
            [start_index, -start_i, -start_j],
            [-start_index, -start_i, start_j],
            [-start_index, start_i, -start_j],
        ]
        for idx in range(1, k):
            wcnf.formula.clauses += [
                [-(start_index + idx), start_index + idx - 1],
                [-(start_index + idx), -(start_i + idx), start_j + idx],
                [-(start_index + idx), start_i + idx, -(start_j + idx)],
                [start_index + idx, -(start_index + idx - 1), start_i + idx,
                start_j + idx],
                [start_index + idx, -(start_index + idx - 1), -(start_i + idx),
                -(start_j + idx)],
            ]
        for idx in range(start_index, start_index + k):
            wcnf.weights[idx] = wcnf.weights[-idx] = 1.0
        wcnf.weights[start_index + k - 1] = np.exp(beta * strength)
    # Add restriction that any x1..xk should be less than q, and add weight 1
    # to all of these variables
    for index in range(n):
        start_index = index * k + 1
        ones = []
        for b, idx in zip(bin(q - 1)[2:], range(start_index, start_index + k)):
            if b == "1":
                ones.append(idx)
            else:
                wcnf.formula.clauses.append([*(-o for o in ones), -idx])
        for idx in range(start_index, start_index + k):
            wcnf.weights[idx] = wcnf.weights[-idx] = 1.0
    return wcnf
