
from ..cnf import CNF
from ..weights import WeightFunction
from ..boolvar import BoolVar

def format_dpmc(cnf: CNF, weight_func: WeightFunction) -> str:
    """ Convert the given weighted CNF formula to the DPMC input format and
        return it as a string """
    text: list[str] = []
    var_index: dict[BoolVar, int] = {}
    var: list[BoolVar] = []
    for i, v in enumerate(weight_func.domain):
        var_index[v] = i
        var.append(v)
    text.append(f"p cnf {len(var_index)} {cnf.num_clauses}")
    vars_string = "".join(str(i) + " " for i in range(1, len(var_index) + 1))
    text.append(f"c p show {vars_string}0")
    for i in range(1, len(var_index) + 1):
        text.append(f"c p weight {i} {weight_func[var[i - 1], True]}")
        text.append(f"c p weight {-i} {weight_func[var[i - 1], False]}")
    for clause in cnf.clauses:
        cur = ""
        for v in clause:
            if not v.value:
                cur += "-"
            cur += str(var_index[v.var] + 1) + " "
        text.append(cur + "0")
    return "\n".join(text)

def format_cachet(cnf: CNF, weight_func: WeightFunction) -> str:
    """ Convert this object to a Cachet formatted string. Assumes that
        weight[v] + weight[-v] = 1 for all variables v in the domain of
        weight_func """
    text: list[str] = []
    var_index: dict[BoolVar, int] = {}
    var: list[BoolVar] = []
    for i, v in enumerate(weight_func.domain):
        var_index[v] = i
        var.append(v)
    # CNF description
    text.append(f"p cnf {len(var_index)} {cnf.num_clauses}")
    # Variable weights
    for i in range(1, len(var_index) + 1):
        text.append(f"w {i} {weight_func[var[i - 1], True]}")
    # Clauses
    for clause in cnf.clauses:
        text.append("".join(map(lambda v: ("-" if not v.value else "") +
        str(var_index[v.var] + 1) + " ", clause)) + "0")
    return "\n".join(text)