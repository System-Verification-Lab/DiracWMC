""" Contains functions to convert wCNF formulae to files in Cachet or DPMC
    format """

from .wcnf import WeightedCNF
from typing import Literal, get_args

WCNFFormat = Literal["cachet", "dpmc"]
WCNF_FORMATS: tuple[str, ...] = get_args(WCNFFormat)

def format_wcnf(formula: WeightedCNF, wcnf_format: WCNFFormat) -> str:
    """ Convert a wCNF formula to a formatted string """
    match wcnf_format:
        case "cachet": return format_cachet(formula)
        case "dpmc": return format_dpmc(formula)
    raise Exception(f"Cannot convert to wCNF format {wcnf_format}")

def format_cachet(formula: WeightedCNF) -> str:
    """ Convert a wCNF formula to a Cachet formatted string """
    text: list[str] = []
    # CNF description
    text.append(f"p cnf {len(formula)} {len(formula.clauses)}")
    # Variable weights
    for i in formula.vars():
        text.append(f"w {i} {formula.get_weight(i)}")
    # Clauses
    for clause in formula.clauses:
        vars_string = "".join(map(lambda i: str(i) + " ", clause))
        text.append(f"{vars_string}0")
    return "\n".join(text)

def format_dpmc(formula: WeightedCNF) -> str:
    """ Convert a wCNF formula to a DPMC formatted string """
    text: list[str] = []
    # CNF description
    text.append(f"p cnf {len(formula)} {len(formula.clauses)}")
    # Sum-vars
    sum_vars = [i for i in formula.vars() if formula.get_weight(i) is not None
    or formula.get_weight(-i) is not None]
    vars_string = "".join(map(lambda i: str(i) + " ", sum_vars))
    text.append(f"c p show {vars_string}0")
    # Variable weights
    for i in formula.signed_vars():
        if i == 0:
            continue
        if formula.get_weight(i) is not None:
            text.append(f"c p weight {i} {formula.get_weight(i)}")
    # Clauses
    for clause in formula.clauses:
        vars_string = "".join(map(lambda i: str(i) + " ", clause))
        text.append(f"{vars_string}0")
    return "\n".join(text)