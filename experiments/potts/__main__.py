
from .converter import standard_potts_to_wcnf_matrix
from .standard_potts_model import StandardPottsModel
from wcnf_matrix import ModelCounter, DPMC, Cachet, TensorOrder, set_var_rep_type, OrderVarRep
import random

SOLVERS: tuple[type[ModelCounter], ...] = (DPMC,)
AVG_OVER_RUNS = 5

# set_var_rep_type(OrderVarRep)

#############################################
# Random regular graph standard Potts model
#############################################

def generate_random_graph(size: int, q: int, expected_degree: float) -> (
StandardPottsModel):
    """ Generate a random regular graph Potts model with interaction strength
        uniformly from [-1, 1]. Given are the size of graph (number of nodes),
        the number of states in the Potts model, and the expected degree of each
        node """
    model = StandardPottsModel(size, q, random.uniform(-1, 1))
    for i in range(size):
        for j in range(i):
            # NOTE: This is technically incorrect (should be expected_degree /
            # (size - 1)), but this is also done this way in Nagy et al.
            if random.uniform(0, 1) < expected_degree / size:
                model.add_interaction(i, j)
    return model

def experiment_random_regular_graph(q: int):
    random.seed(42)
    for solver in SOLVERS:
        model_counter = solver()
        print(f"\nRandom graph {solver.__name__} (q={q}):")
        for size in range(8, 70, 4):
            models = [generate_random_graph(size, q, 4) for _ in
            range(AVG_OVER_RUNS)]
            problems = [standard_potts_to_wcnf_matrix(model).trace_formula() for
            model in models]
            failed = False
            runtime = 0.0
            for result in model_counter.batch_model_count(*problems):
                if not result.success:
                    failed = True
                    break
                runtime += result.runtime
            if failed:
                print("FAILURE")
                break
            print(f"({size}, {runtime / AVG_OVER_RUNS})", end=" ", flush=True)
        print()

def experiment_random_regular_graph_accuracy(q: int):
    random.seed(42)
    for solver in SOLVERS:
        model_counter = solver()
        print(f"\nRandom graph accuracy {solver.__name__} (q={q}):")
        for size in range(2, 10):
            models = [generate_random_graph(size, q, 4) for _ in
            range(AVG_OVER_RUNS)]
            problems = [standard_potts_to_wcnf_matrix(model).trace_formula() for
            model in models]
            failed = False
            error = 0.0
            for result, model in zip(model_counter.batch_model_count(*problems),
            models):
                if not result.success:
                    failed = True
                    break
                error += abs(result.model_count / model.partition_function() -
                1)
            if failed:
                print("FAILURE")
                break
            print(f"({size}, {error / AVG_OVER_RUNS})", end=" ", flush=True)
        print()

#############################################

for q in range(2, 4):
    experiment_random_regular_graph_accuracy(q)
for q in range(2, 9):
    experiment_random_regular_graph(q)