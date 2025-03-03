""" Reproduce square lattice experiments from https://arxiv.org/pdf/2212.12812
    """

from ..generators.ising import generate_square_lattice
from ._utils import do_ising_experiment
from ..wcnf.solver import SOLVERS, SolverType

def run():
    """ Run all square lattice Ising experiments and print results to console
        """
    results: dict[SolverType, list[tuple[int, float]]] = {}
    for solver_type in SOLVERS:
        results[solver_type] = []
        side_length = 2
        timed_out = False
        while not timed_out:
            model = generate_square_lattice(side_length)
            cur = do_ising_experiment(f"Square lattice l={side_length}; "
            f"solver={solver_type}", model, solver_type)
            if cur < 0.0:
                timed_out = True
            else:
                results[solver_type].append((side_length, cur))
            side_length += 1
    for solver_type, res in results.items():
        print(f"Results for solver {solver_type}:")
        print(" ".join(f"({r[0]}, {r[1]})" for r in res))