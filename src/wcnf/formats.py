""" Contains functions to convert wCNF formulae to files in Cachet or DPMC
    format """

from .wcnf import WeightedCNF
from typing import Literal, get_args

WCNFFormat = Literal["cachet", "dpmc"]
WCNF_FORMATS: tuple[str] = get_args(WCNFFormat)

def format_wcnf(formula: WeightedCNF, wcnf_format: WCNFFormat) -> str:
    """ Convert a wCNF formula to a formatted string """
    match wcnf_format:
        case "cachet": return format_cachet(formula)
        case "dpmc": return format_dpmc(formula)
    raise Exception(f"Cannot convert to wCNF format {wcnf_format}")

def format_cachet(formula: WeightedCNF) -> str:
    """ Convert a wCNF formula to a Cachet formatted string """
    ...

def format_dpmc(formula: WeightedCNF) -> str:
    """ Convert a wCNF formula to a DPMC formatted string """
    ...