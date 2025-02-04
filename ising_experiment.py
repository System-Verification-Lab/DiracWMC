""" This file contains experiments for reproducing results from the paper
    https://arxiv.org/pdf/2212.12812 """

import random
from typing import Iterable
from src.models import IsingModel
from src.converters import ising_to_wcnf
from src.wcnf import SolverInterface, SolverType, SOLVERS
from src.logger import ConsoleColor

def do_experiment(name: str, model: IsingModel, solver: SolverType, *, beta:
float = 1.0) -> float:
    """ Perform an experiment and display runtime, given the name of the
        experiment, the model, and the solver to use. Returns the runtime """
    formula = ising_to_wcnf(model, beta)
    solver_interface = SolverInterface.from_solver_name(solver)
    _ = solver_interface.calculate_weight(formula)
    runtime = solver_interface.runtime
    print()
    print(f"{ConsoleColor.GREEN}Runtime of experiment \"{name}\": {runtime} "
    f"s{ConsoleColor.CLEAR}")
    print()
    return runtime

def square_lattice_connections(l: int) -> Iterable[tuple[int, int]]:
    """ Get all connection pairs in a square lattice with linear size l. Nodes
        are indexed from 0 to l*l-1 """
    for i in range(l * l):
        if i + l < l * l:
            yield (i, i + l)
        if i % l != l - 1:
            yield (i, i + 1)

def do_square_lattice_experiment(solver: SolverType, l: int) -> float:
    """ Perform an experiment with a square lattice with linear size l and
        inverse temperature beta=1. Returns the runtime """
    model = IsingModel(l * l)
    for i, j in square_lattice_connections(l):
        strength = random.normalvariate(0, 1)
        model.add_interaction(i, j, strength)
    return do_experiment(f"Square lattice; Solver {solver}; Linear size {l}",
    model, solver)

# Two-dimensional lattice with linear size l at beta=1, with standard normal
# distributed edge weights
# dpmc_results: list[tuple[int, float]] = []
# for l in range(2, 16):
#     dpmc_results.append((l, do_square_lattice_experiment("dpmc", l)))
# cachet_results: list[tuple[int, float]] = []
# for l in range(2, 10):
#     cachet_results.append((l, do_square_lattice_experiment("cachet", l)))
tensororder_results: list[tuple[int, float]] = []
for l in range(2, 21):
    tensororder_results.append((l, do_square_lattice_experiment("tensororder", l)))

# print("DPMC results:")
# print(" ".join(f"({l}, {r})" for l, r in dpmc_results))
# print("Cachet results:")
# print(" ".join(f"({l}, {r})" for l, r in cachet_results))
print("TensorOrder results:")
print(" ".join(f"({l}, {r})" for l, r in tensororder_results))
