
from .cnf import CNF
from .weights import WeightFunction
from ...wcnf.formula import WeightedCNFFormula, CNFFormula, VariableWeights

def pack_wcnf_formula(cnf: CNF, weight_func: WeightFunction) -> (
WeightedCNFFormula):
    var_index = {var: i for i, var in enumerate(weight_func.domain, 1)}
    n = len(var_index)
    new_cnf = CNFFormula(n)
    for clause in cnf._clauses:
        cur = []
        for var in clause:
            cur.append(var_index[var.var] if var.value else -var_index[var.var])
        new_cnf.clauses.append(cur)
    new_weights = VariableWeights(n, weights={i: weight_func[var, True] for var,
    i in var_index.items()} | {-i: weight_func[var, False] for var, i in
    var_index.items()})
    return WeightedCNFFormula(len(var_index), formula=new_cnf,
    weights=new_weights)