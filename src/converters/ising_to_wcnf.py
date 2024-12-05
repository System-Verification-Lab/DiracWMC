
from ..models.ising import IsingModel
from ..wcnf import WeightedCNF
import numpy as np

def ising_to_wcnf(model: IsingModel, beta: float) -> WeightedCNF:
    """ Converts an Ising model to a weighted CNF formula, such that the
        weighted model count of the CNF formula is equal to the partition
        function of the Ising model, given inverse temperature beta. This
        procedure is described in https://arxiv.org/abs/2212.12812 """
    # Indices 1,..,n correspond with nodes, n+1,..,m with interactions
    n = model.node_count
    formula = WeightedCNF(n + len(model.interactions))
    # For every interaction, add clause ((i <=> j) <=> ij)
    interactions = list(model.interactions.items())
    for index, ((i, j), _) in enumerate(interactions, n + 1):
        # Variables in wCNF are 1-indexed
        i, j = i + 1, j + 1
        formula.clauses += [[i, -j, -index], [i, j, index], [-i, j, -index],
        [-i, -j, index]]
    # Weight of variables is e^(beta*external[i]*(2*tau[i]-1)), where tau[i] is
    # 0 or 1 and indices truth value of variable i
    for index in range(1, n + 1):
        external_field = model.external_field[index - 1]
        formula.set_weight(index, np.exp(beta * external_field))
        formula.set_weight(-index, np.exp(-beta * external_field))
    # Weight of connections is e^(beta*strength*(2*tau[ij]-1))
    for index, (_, strength) in enumerate(interactions, n + 1):
        formula.set_weight(index, np.exp(beta * strength))
        formula.set_weight(-index, np.exp(-beta * strength))
    return formula