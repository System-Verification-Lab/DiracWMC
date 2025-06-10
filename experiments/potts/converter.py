
from .standard_potts_model import StandardPottsModel
from wcnf_matrix import WCNFMatrix, Index, Reg, get_var_rep_type, BoolVar, WeightFunction
import numpy as np

def standard_potts_to_wcnf_matrix(model: StandardPottsModel, beta: float = 1.0
) -> WCNFMatrix:
    """ Convert a standard potts model to a weighted CNF formula, such that the
        partition function of the model is equal to the total weight of the
        formula """
    n, q = model.sites, model.states
    index = Index(q)
    regs = [Reg(index) for _ in range(n)]
    mat = WCNFMatrix.identity(index, n) | regs
    a, b = get_var_rep_type()(q), get_var_rep_type()(q)
    c = BoolVar()
    cnf, aux_vars = a.equals_other_to_var(b, c)
    weight_func = WeightFunction([*a.domain(), *b.domain(), c, *aux_vars])
    weight_func.fill(1.0)
    weight_func[c, True] = np.exp(beta * model.interaction_strength)
    eq_matrix = WCNFMatrix(index, cnf, weight_func, [a, b], [a, b])
    for i, j in model.interactions():
        mat *= eq_matrix | (regs[i], regs[j])
    return mat.mat
