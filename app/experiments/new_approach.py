""" Determine the two spin partition function using a new approach """

from ..wcnf.formula import WeightedCNFFormula, CNFFormula, VariableWeights
from ..wcnf.solvers import DPMCSolver, SolverResult
from ..models import QuantumIsingModel
from sympy import Symbol, And, Equivalent, Or, Not
from sympy.logic.boolalg import BooleanFunction
from itertools import product
from time import time

SOLVER_TIMEOUT = 1.0
TOTAL_TIMEOUT = 1.0
ERROR_THRESHOLD = 1e-13

def run():
    # Calculate true value
    model = QuantumIsingModel(2, interaction={(0, 1): 1.0},
    external_field_x=1.0)
    true_weight = model.partition_function(1.0)
    # Run experiments
    powers = 3
    timed_out = False
    results = []
    while not timed_out:
        result = run_for_powers(powers, true_weight)
        if result is None:
            timed_out = True
        else:
            results.append(result)
        powers += 1
    print()
    print("Results:")
    print(" ".join(f"({e},{r})" for e, r in results))
    print()

def run_for_powers(powers: int, true_weight: float) -> (tuple[float, float] |
None):
    """ Returns (error, runtime) """
    weight = 0.0
    fac = 1.0
    runtime = 0.0
    for power in range(powers):
        # Quit on timeout
        result = get_power_trace(power)
        runtime += result.runtime
        if not result.success or runtime > TOTAL_TIMEOUT:
            return None
        weight += result.total_weight / fac
        fac *= power + 1
    error = abs(weight / true_weight - 1.0)
    if error < ERROR_THRESHOLD:
        return None
    print()
    print(f"Trace approximation for powers={powers}:", weight)
    print("Error:", error)
    print("Runtime:", runtime, "s")
    print()
    return (error, runtime)

def one_of(*symbols: Symbol) -> BooleanFunction:
    assert len(symbols) > 0
    if len(symbols) == 1:
        return symbols[0]
    clauses = []
    for i, j in product(range(len(symbols)), repeat=2):
        if i >= j:
            continue
        clauses.append(~symbols[i] | ~symbols[j])
    clauses.append(Or(*symbols))
    return And(*clauses)

def get_power_trace(power: int, *, print_result: bool = False) -> SolverResult:
    if power == 0:
        return SolverResult(True, 0.0, 4.0)
    boolfunc = Equivalent(Symbol("q1,0"), Symbol(f"q1,{power}"))
    boolfunc &= Equivalent(Symbol("q2,0"), Symbol(f"q2,{power}"))
    for i in range(power):
        boolfunc &= Equivalent(Symbol(f"r1,{i}"), Symbol(f"b3,{i}") &
        Symbol(f"q1,{i}"))
        boolfunc &= Equivalent(Symbol(f"r2,{i}"), Symbol(f"b2,{i}") &
        Symbol(f"q2,{i}"))
        boolfunc &= Equivalent(Symbol(f"q1,{i+1}"), Symbol(f"q1,{i}") ^
        Symbol(f"b2,{i}"))
        boolfunc &= Equivalent(Symbol(f"q2,{i+1}"), Symbol(f"q2,{i}") ^
        Symbol(f"b1,{i}"))
        boolfunc &= one_of(*(Symbol(f"b{j},{i}") for j in range(1, 4)))
    formula, indices = CNFFormula.from_sympy(boolfunc)
    weights = VariableWeights(len(formula))
    for i in range(power + 1):
        weights[indices[f"q1,{i}"]] = weights[-indices[f"q1,{i}"]] = 1
        weights[indices[f"q2,{i}"]] = weights[-indices[f"q2,{i}"]] = 1
    for i in range(power):
        weights[indices[f"b1,{i}"]] = weights[-indices[f"b1,{i}"]] = 1
        weights[indices[f"b2,{i}"]] = weights[-indices[f"b2,{i}"]] = 1
        weights[indices[f"b3,{i}"]] = weights[-indices[f"b3,{i}"]] = 1
        weights[indices[f"r1,{i}"]] = -1
        weights[-indices[f"r1,{i}"]] = 1
        weights[indices[f"r2,{i}"]] = -1
        weights[-indices[f"r2,{i}"]] = 1
    wcnf = WeightedCNFFormula(len(formula), formula=formula, weights=weights)
    solver = DPMCSolver(timeout=SOLVER_TIMEOUT)
    result = solver.run_solver(wcnf)
    print("Solver runtime:", result.runtime)
    if print_result:
        print(f"Solver result for power={power}")
        print(result)
        print()
    return result