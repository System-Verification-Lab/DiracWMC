
from .models import IsingModel, QuantumIsingModel
from .wcnf.formula import WeightedCNFFormula, CNFFormula
import numpy as np
import math
from itertools import product
from sympy import Symbol
from sympy.logic.boolalg import (BooleanFunction, BooleanTrue, And, Or, Implies,
Equivalent)

def ising_to_wcnf(model: IsingModel, beta: float) -> WeightedCNFFormula:
    """ Converts an Ising model to a weighted CNF formula, such that the
        weighted model count of the CNF formula is equal to the partition
        function of the Ising model, given inverse temperature beta. This
        procedure is described in https://arxiv.org/abs/2212.12812. The first
        len(model) variables in the output correspond with nodes, the other with
        interactions """
    # Indices 1,..,n correspond with nodes, n+1,..,m with interactions
    n = len(model)
    interactions = list(model.interactions())
    wcnf = WeightedCNFFormula(n + len(interactions))
    # For every interaction, add clause ((i <=> j) <=> ij)
    for index, (i, j, _) in enumerate(interactions, n + 1):
        # Variables in wCNF are 1-indexed
        i, j = i + 1, j + 1
        wcnf.formula.clauses += [[i, -j, -index], [i, j, index], [-i, j,
        -index], [-i, -j, index]]
    # Weight of variables is e^(beta*external[i]*(2*tau[i]-1)), where tau[i] is
    # 0 or 1 and indices truth value of variable i
    for index in range(1, n + 1):
        external_field = model.external_field[index - 1]
        wcnf.weights[index] = np.exp(beta * external_field)
        wcnf.weights[-index] = np.exp(-beta * external_field)
    # Weight of connections is e^(beta*strength*(2*tau[ij]-1))
    for index, (_, _, strength) in enumerate(interactions, n + 1):
        wcnf.weights[index] = np.exp(beta * strength)
        wcnf.weights[-index] = np.exp(-beta * strength)
    return wcnf

def quantum_ising_to_ising(quantum_model: QuantumIsingModel, beta: float,
layers: int) -> tuple[IsingModel, float]:
    """ Converts a d-dimensional Quantum Ising Model to a (d+1)-dimensional
        Ising Model. The partition functions of the two models are equivalent at
        inverse temperate beta for the Quantum Ising Model, and inverse
        temperature 1 for the Ising Model. The multiplication factor between the
        two models is returned as the second item in the tuple. This is the
        multiplication factor *per spin* in the output Ising model. Increasing
        the number of layers increases the accuracy of the estimation.
        Implementation is based on Theorem 4 from
        https://academic.oup.com/ptp/article/56/5/1454/1860476. Nodes are
        indexed `layer * QUANTUM_NODE_COUNT + quantum_node_index`
        """
    assert beta > 0
    assert quantum_model.external_field_z == 0.0
    assert quantum_model.external_field_x >= 0.0
    if quantum_model.external_field_x == 0.0:
        return _trivial_quantum_conversion(quantum_model, beta), 1.0
    assert layers > 2
    gamma = beta * quantum_model.external_field_x
    inter_layer_strength = np.log(_coth(gamma / layers)) / 2.0
    node_count = len(quantum_model)
    model = IsingModel(layers * node_count)
    # Interactions inside layers
    interactions = list(quantum_model.interactions())
    for layer, interaction in product(range(layers), interactions):
        i, j, strength = interaction
        model.set_interaction(layer * node_count + i, layer * node_count + j,
        beta * strength / layers)
    # Interactions between layers
    for layer, i in product(range(layers), range(node_count)):
        model.set_interaction(layer * node_count + i, (layer + 1) % layers *
        node_count + i, inter_layer_strength)
    # NOTE: The output model does not have an external field
    factor = math.sqrt(np.sinh(2.0 * gamma / layers) / 2.0)
    return model, factor

def _coth(x: float) -> float:
    """ Hyperbolic cotangent """
    return np.cosh(x) / np.sinh(x)

def _trivial_quantum_conversion(quantum_model: QuantumIsingModel, beta: float
) -> IsingModel:
    """ Conversion of a Quantum Ising Model to an Ising model, in the trivial
        case where the external factors is 0. The output model will have the
        same number of nodes as the input model. Output model will have all
        interaction strengths multiplied by beta """
    assert quantum_model.external_factor == 0.0
    model = IsingModel(quantum_model.node_count)
    for (i, j), strength in quantum_model.interactions.items():
        model.add_interaction(i, j, strength * beta)
    return model

def quantum_ising_to_wcnf(quantum_model: QuantumIsingModel, beta: float, layers:
int) -> WeightedCNFFormula:
    """ Approximate a quantum Ising model with a weighted CNF formula at the
        given inverse temperature beta, using the given number of layers to
        approximate the model """
    model, factor = quantum_ising_to_ising(quantum_model, beta, layers)
    wcnf = ising_to_wcnf(model, 1.0)
    for i in range(1, len(model) + 1):
        wcnf.weights[i] *= factor
        wcnf.weights[-i] *= factor
    return wcnf

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