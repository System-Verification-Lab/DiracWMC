
from .ising_model import IsingModel
from wcnf_matrix import CNF, WeightFunction, BoolVar, WCNFMatrix
import numpy as np

def ising_to_wcnf(model: IsingModel, beta: float = 1.0) -> tuple[CNF,
WeightFunction]:
    """ Convert the given Ising model to a CNF formula and weight function,
        such that the weighted model count of the formula w.r.t. the weight
        function is equal to the partition function of the Ising model at
        inverse temperature beta """
    # Indices 0,..,n-1 correspond with nodes, n,..,m+n-1 with interactions
    n = len(model)
    interactions = list(model.interactions())
    bool_vars = [BoolVar() for _ in range(n + len(interactions))]
    cnf = CNF()
    weight_func = WeightFunction(bool_vars)
    # For every interaction, add clause ((i <=> j) <=> ij)
    for index, (i, j, _) in enumerate(interactions, n):
        cnf.add_clause(
            [bool_vars[i], -bool_vars[j], -bool_vars[index]],
            [bool_vars[i], bool_vars[j], bool_vars[index]],
            [-bool_vars[i], bool_vars[j], -bool_vars[index]],
            [-bool_vars[i], -bool_vars[j], bool_vars[index]],
        )
    # Weight of variables is e^(beta*external[i]*(2*tau[i]-1)), where tau[i] is
    # 0 or 1 and indices truth value of variable i
    for index, external_field in enumerate(model.external_field):
        weight_func[bool_vars[index], True] = np.exp(beta * external_field)
        weight_func[bool_vars[index], False] = np.exp(-beta * external_field)
    # Weight of connections is e^(beta*strength*(2*tau[ij]-1))
    for index, (_, _, strength) in enumerate(interactions, n):
        weight_func[bool_vars[index], True] = np.exp(beta * strength)
        weight_func[bool_vars[index], False] = np.exp(-beta * strength)
    return cnf, weight_func

def ising_to_wcnf_matrix(model: IsingModel, beta: float = 1.0) -> WCNFMatrix:
    """ Convert the given Ising model to a WCNFMatrix, the trace of which is
        equal to the partition function of the Ising model at inverse
        temperature beta """
    ...