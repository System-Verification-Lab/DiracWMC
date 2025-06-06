
from .converter import ising_to_wcnf, ising_to_wcnf_matrix
from .ising_model import IsingModel
from wcnf_matrix import ModelCounter, DPMC, Cachet, TensorOrder
import random

SOLVERS: tuple[type[ModelCounter], ...] = (DPMC, Cachet, TensorOrder,)
AVG_OVER_RUNS = 5
random.seed(42)

#############################################
# Square lattice Ising model
#############################################

def generate_square_lattice(size: int) -> IsingModel:
    """ Generate a square lattice Ising model with interaction and external
        field strengths from the standard normal distribution. The side length
        is given by size """
    model = IsingModel(size * size)
    # Interaction strengths
    for i in range(size * size):
        if i + size < size * size:
            strength = random.normalvariate()
            model[i, i + size] = strength
        if i % size != size - 1:
            strength = random.normalvariate()
            model[i, i + 1] = strength
    # External field strengths
    for i in range(size * size):
        model[i] = random.normalvariate(0, 1)
    return model

def experiment_square_lattice(use_matrix: bool = False):
    for solver in SOLVERS:
        model_counter = solver()
        print(f"\nSquare lattice {solver.__name__} (matrix={use_matrix}):")
        for size in range(2, 23):
            models = [generate_square_lattice(size) for _ in
            range(AVG_OVER_RUNS)]
            if use_matrix:
                problems = [ising_to_wcnf_matrix(model).trace_formula() for
                model in models]
            else:
                problems = [ising_to_wcnf(model) for model in models]
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

def experiment_square_lattice_accuracy(use_matrix: bool = False):
    for solver in SOLVERS:
        model_counter = solver()
        print(f"\nSquare lattice accuracy {solver.__name__} (matrix="
        f"{use_matrix}):")
        for size in range(2, 5):
            models = [generate_square_lattice(size) for _ in
            range(AVG_OVER_RUNS)]
            if use_matrix:
                problems = [ising_to_wcnf_matrix(model).trace_formula() for
                model in models]
            else:
                problems = [ising_to_wcnf(model) for model in models]
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

experiment_square_lattice()
experiment_square_lattice_accuracy()
experiment_square_lattice(use_matrix=True)
experiment_square_lattice_accuracy(use_matrix=True)