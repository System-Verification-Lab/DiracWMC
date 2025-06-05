
from .ising_model import IsingModel
from wcnf_matrix import CNF, WeightFunction, BoolVar, WCNFMatrix, Reg, Index
import numpy as np
from functools import reduce

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

def exp_z_rotation(theta: float, index: Index) -> WCNFMatrix[float]:
    """ Returns a Z-rotation matrix with angle theta"""
    x = BoolVar()
    weight_func = WeightFunction([x], weights={
        x: (np.exp(theta), np.exp(-theta))
    })
    return WCNFMatrix(index, CNF(), weight_func, [x], [x])

def exp_zz_rotation(theta: float, index: Index) -> WCNFMatrix[float]:
    """ Returns a ZZ-rotation matrix with angle theta """
    x, y, r = BoolVar(), BoolVar(), BoolVar()
    cnf = CNF([
        [x, -y, -r],
        [x, y, r],
        [-x, y, -r],
        [-x, -y, r],
    ])
    weight_func = WeightFunction([x, y, r])
    weight_func.fill(1.0)
    weight_func[r, 0] = np.exp(-theta)
    weight_func[r, 1] = np.exp(theta)
    return WCNFMatrix(index, cnf, weight_func, [x, y], [x, y])

def ising_to_wcnf_matrix(model: IsingModel, beta: float = 1.0) -> WCNFMatrix:
    """ Convert the given Ising model to a WCNFMatrix, the trace of which is
        equal to the partition function of the Ising model at inverse
        temperature beta """
    index = Index()
    n = len(model)
    regs = [Reg(index) for _ in range(n)]
    interactions = reduce(lambda x, y: x * y, (exp_zz_rotation(beta * strength,
    index) | (regs[i], regs[j]) for i, j, strength in model.interactions()))
    external_field = reduce(lambda x, y: x * y, (exp_z_rotation(beta * strength,
    index) | regs[i] for i, strength in enumerate(model.external_field)))
    return (interactions * external_field).mat