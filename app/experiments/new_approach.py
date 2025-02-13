""" Determine the two spin partition function using a new approach """

from ..wcnf.formula import WeightedCNFFormula

APPROX_TERMS = 4

def run():
    total = 0.0
    fac = 1.0
    for power in range(APPROX_TERMS):
        total += get_power_trace(power) / fac
        fac *= power + 1
    print("Trace approximation:", total)

def get_power_trace(power: int) -> float:
    if power == 0:
        return 4.0
    num_vars = 2 * (power + 1) + 3 * power + 2 * power
    ...
    wcnf = WeightedCNFFormula()