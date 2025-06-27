
from .quantum_ising_model import QuantumIsingModel
from wcnf_matrix import CNF, WeightFunction, BoolVar, WCNFMatrix, Reg, Index, LogVarRep, value
import numpy as np
from functools import reduce
import math

SQRT2 = math.sqrt(2)

def exp_z_rotation(theta: float, index: Index) -> WCNFMatrix[float]:
    """ Returns a Z-rotation matrix with angle theta """
    x = BoolVar()
    weight_func = WeightFunction([x], weights={
        x: (np.exp(theta), np.exp(-theta))
    })
    return WCNFMatrix(index, CNF(), weight_func, [LogVarRep(2, [x])],
    [LogVarRep(2, [x])])

def exp_zz_rotation(theta: float, index: Index) -> WCNFMatrix[float]:
    """ Returns a ZZ-rotation matrix with angle theta """
    x, y, r = BoolVar(), BoolVar(), BoolVar()
    # r <-> (x <-> y)
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
    x, y = LogVarRep(2, [x]), LogVarRep(2, [y])
    return WCNFMatrix(index, cnf, weight_func, [x, y], [x, y])

def hadamard(index: Index) -> WCNFMatrix:
    """ Returns a Hadamard matrix on the given index """
    x, y, r = BoolVar(), BoolVar(), BoolVar()
    # r <-> (x AND y)
    cnf = CNF([
        [-r, x],
        [-r, y],
        [r, -x, -y],
    ])
    weight_func = WeightFunction([x, y, r])
    weight_func.fill(1.0)
    weight_func[r, 0] = 1.0 / SQRT2
    weight_func[r, 1] = -1.0 / SQRT2
    x, y = LogVarRep(2, [x]), LogVarRep(2, [y])
    return WCNFMatrix(index, cnf, weight_func, [x], [y])

def identity(index: Index) -> WCNFMatrix:
    """ Returns an identity matrix on the given index """
    x = BoolVar()
    cnf = CNF()
    weight_func = WeightFunction([x])
    weight_func.fill(1.0)
    x = LogVarRep(2, [x])
    return WCNFMatrix(index, cnf, weight_func, [x], [x])

def quantum_ising_to_wcnf(model: QuantumIsingModel, beta: float = 1.0,
trotter_layers: int = 5) -> tuple[CNF, WeightFunction]:
    """ Convert the given quantum Ising model to a CNF formula and weight
        function (approximation) using trotterization. Thwe ighted model count
        of the formula w.r.t. the weight function approximates the partition
        function of the quantum Ising model at inverse temperature beta """
    index = Index()
    n = len(model)
    regs = [Reg(index) for _ in range(n)]
    ident = reduce(lambda x, y: x * y, (identity(index) | reg for reg in regs))
    # Z-direction
    if len(list(model.interactions())) == 0:
        interactions = ident
    else:
        interactions = reduce(lambda x, y: x * y, (exp_zz_rotation(beta *
        strength / trotter_layers, index) | (regs[i], regs[j]) for i, j, strength in
        model.interactions()))
    external_field_z = reduce(lambda x, y: x * y, (exp_z_rotation(beta *
    model.external_field_z / trotter_layers, index) | reg for reg in regs))
    # Hadamards
    hadamards = reduce(lambda x, y: x * y, (hadamard(index) | reg for reg in
    regs))
    # X-direction
    external_field_x = reduce(lambda x, y: x * y, (exp_z_rotation(beta *
    model.external_field_x / trotter_layers, index) | regs[i] for i in
    range(n)))
    # Calculate final matrix
    cur = ident
    for _ in range(trotter_layers):
        cur *= (interactions * external_field_z * hadamards * external_field_x *
        hadamards)
    return cur.mat.trace_formula()