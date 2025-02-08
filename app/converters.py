
from .models import IsingModel
from .wcnf.formula import WeightedCNFFormula
import numpy as np

def ising_to_wcnf(model: IsingModel, beta: float) -> WeightedCNFFormula:
    """ Converts an Ising model to a weighted CNF formula, such that the
        weighted model count of the CNF formula is equal to the partition
        function of the Ising model, given inverse temperature beta. This
        procedure is described in https://arxiv.org/abs/2212.12812 """
    # Indices 1,..,n correspond with nodes, n+1,..,m with interactions
    n = len(model)
    interactions = list(model.interactions())
    wcnf = WeightedCNFFormula(n + len(interactions))
    # For every interaction, add clause ((i <=> j) <=> ij)
    for index, (i, j, _) in enumerate(interactions, n + 1):
        # Variables in wCNF are 1-indexed
        i, j = i + 1, j + 1
        wcnf.formula.clauses += [[i, -j, -index], [i, j, index], [-i, j,
        -index], [-i, -j, index]]
    # Weight of variables is e^(beta*external[i]*(2*tau[i]-1)), where tau[i] is
    # 0 or 1 and indices truth value of variable i
    for index in range(1, n + 1):
        external_field = model.external_field[index - 1]
        wcnf.weights[index] = np.exp(beta * external_field)
        wcnf.weights[-index] = np.exp(-beta * external_field)
    # Weight of connections is e^(beta*strength*(2*tau[ij]-1))
    for index, (_, _, strength) in enumerate(interactions, n + 1):
        wcnf.weights[index] = np.exp(beta * strength)
        wcnf.weights[-index] = np.exp(-beta * strength)
    return wcnf