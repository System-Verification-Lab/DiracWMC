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

def all_square_lattice_experiments(solver: SolverType) -> list[tuple[int,
float]]:
    """ Perform all square lattice experiments for a specific solver. Halts
        whenever a solver times out. Square lattice has linear size l starting
        from 2,3,... with beta=1 """
    results: list[tuple[int, float]] = []
    l = 2
    timed_out = False
    while not timed_out:
        try:
            results.append((l, do_square_lattice_experiment(solver, l)))
        except:
            timed_out = True
        l += 1
    return results

results: dict[SolverType, list[tuple[int, float]]] = {}
for solver in SOLVERS:
    results[solver] = all_square_lattice_experiments(solver)

for solver, res in results.items():
    print(f"{solver} results:")
    print(" ".join(f"({l}, {r})" for l, r in res))
