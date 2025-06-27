
from .converter import quantum_ising_to_wcnf
from .quantum_ising_model import QuantumIsingModel
from wcnf_matrix import ModelCounter, DPMC, Cachet, TensorOrder
import random
from typing import Iterable

# NOTE: Cachet and TensorOrder cannot handle negative weights
SOLVERS: tuple[type[ModelCounter], ...] = (DPMC,)
AVG_OVER_RUNS = 5
BETA = 1.0

#############################################
# Random regular graph quantum Ising model
#############################################

def generate_random_graph(size: int, expected_degree: float) -> (
QuantumIsingModel):
    """ Generate a random regular graph quantum Ising model with interaction
        strengths and external field strengths from the standard normal
        distribution. Given are the size of graph (number of nodes) and the
        expected degree of each node """
    model = QuantumIsingModel(size)
    for i in range(size):
        for j in range(i):
            # NOTE: This is technically incorrect (should be expected_degree /
            # (size - 1)), but this is also done this way in Nagy et al.
            if random.uniform(0, 1) < expected_degree / size:
                model[i, j] = random.normalvariate()
    model.external_field_x = random.normalvariate()
    model.external_field_z = random.normalvariate()
    return model

def experiment_random_regular_graph(size: int, layers: Iterable[int]):
    random.seed(42)
    for solver in SOLVERS:
        model_counter = solver()
        print(f"\nRandom graph {solver.__name__} (size={size}); reporting "
        "(error, runtime):")
        models = [generate_random_graph(size, 3) for _ in
        range(AVG_OVER_RUNS)]
        true_values = [model.partition_function(BETA) for model in models]
        for trotter_layers in layers:
            problems = [quantum_ising_to_wcnf(model, BETA, trotter_layers) for
            model in models]
            failed = False
            runtime = 0.0
            error = 0.0
            for result, true_value in zip(model_counter.batch_model_count(
            *problems), true_values):
                if not result.success:
                    failed = True
                    break
                runtime += result.runtime
                error += abs(result.model_count / true_value - 1)
            if failed:
                print("FAILURE")
                break
            print(f"({error / AVG_OVER_RUNS}, {runtime / AVG_OVER_RUNS})",
            end=" ", flush=True)
        print()

#############################################

experiment_random_regular_graph(6, range(5, 200, 5))