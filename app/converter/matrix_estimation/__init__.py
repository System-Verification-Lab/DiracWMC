
from ...quantum_ising import QuantumIsingModel
from ...wcnf import WeightedCNFFormula
from sympy import Symbol
from sympy.logic.boolalg import (BooleanFunction, BooleanTrue, Equivalent,
Implies, And, Or)
from itertools import product

def matrix_quantum_ising_to_wcnf(quantum_model: QuantumIsingModel, beta: float,
terms: int) -> WeightedCNFFormula:
    """ Approximate a quantum Ising model with a weighted CNF formula at the
        given inserse temperate beta, using the given number of terms in the
        matrix exponential approximation """
    assert terms > 0
    formula: BooleanFunction = BooleanTrue()
    # Maps variable names to negative and positive weight respectively
    weights: dict[str, tuple[float, float]] = {}
    for i in range(terms):
        layer_formula, layer_weights, controls = _matrix_layer_formula(
        quantum_model, beta, i)
        formula &= layer_formula
        weights = {**weights, **layer_weights}
        weights[f"i{i}"] = (1.0, 1.0 / (i + 1))
        if i > 0:
            formula &= Implies(Symbol(f"i{i}"), Symbol(f"i{i-1}"))
        formula &= Implies(Symbol(f"i{i}"), _one_of(*controls))
        formula &= Implies(~Symbol(f"i{i}"), _none_of(*controls))
    # For trace: link starting variables with end variables
    for i in range(len(quantum_model)):
        formula &= Equivalent(Symbol(f"q0,{i}"), Symbol(f"q{terms},{i}"))
    return WeightedCNFFormula.from_sympy(formula, weights)

def _matrix_layer_formula(quantum_model: QuantumIsingModel, beta: float, index:
int) -> tuple[BooleanFunction, dict[str, tuple[float, float]], list[Symbol]]:
    """ Create a formula and weights function for one layer in the matrix
        exponent approximation. Returns a tuple of the CNF formula, a map
        from variable names to negative and positive weights, and a list of
        control variables """
    controls: list[Symbol] = []
    mults: list[Symbol] = []
    weights: dict[str, tuple[float, float]] = {}
    formula: BooleanFunction = BooleanTrue()
    # Interactions
    for i, j, strength in quantum_model.interactions():
        control = Symbol(f"c{index},{len(controls)}")
        controls.append(control)
        weights[control.name] = (1.0, beta * strength)
        mult_a = Symbol(f"r{index},{len(mults)}")
        mults.append(mult_a)
        mult_b = Symbol(f"r{index},{len(mults)}")
        mults.append(mult_b)
        formula &= Equivalent(mult_a, control & Symbol(f"q{index},{i}"))
        formula &= Equivalent(mult_b, control & Symbol(f"q{index},{j}"))
    # Z-directed external field
    if quantum_model.external_field_z != 0.0:
        for i in range(len(quantum_model)):
            control = Symbol(f"c{index},{len(controls)}")
            controls.append(control)
            weights[control.name] = (1.0, quantum_model.external_field_z * beta)
            mult = Symbol(f"r{index},{len(mults)}")
            mults.append(mult)
            formula &= Equivalent(mult, control & Symbol(f"q{index},{i}"))
    # X-directed external field
    for i in range(len(quantum_model)):
        control = Symbol(f"c{index},{len(controls)}")
        controls.append(control)
        weights[control.name] = (1.0, quantum_model.external_field_x * beta)
        formula &= Equivalent(Symbol(f"q{index+1},{i}"), control ^
        Symbol(f"q{index},{i}"))
    for mult in mults:
        weights[mult.name] = (1.0, -1.0)
    for i in range(len(quantum_model)):
        weights[f"q{index},{i}"] = (1.0, 1.0)
        weights[f"q{index+1},{i}"] = (1.0, 1.0)
    return formula, weights, controls

def _one_of(*symbols: Symbol) -> BooleanFunction:
    """ Create a sympy boolean formula which is true when one of the symbols is
        true """
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

def _none_of(*symbols: Symbol) -> BooleanFunction:
    """ Create a sympy boolean formula which is true when none of the symbols
        are true """
    assert len(symbols) > 0
    return And(*(~symbol for symbol in symbols))