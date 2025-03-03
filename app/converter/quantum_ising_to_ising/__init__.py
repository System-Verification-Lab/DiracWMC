
from ...ising import IsingModel
from ...quantum_ising import QuantumIsingModel
import math
import numpy as np
from itertools import product

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