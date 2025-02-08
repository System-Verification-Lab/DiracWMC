""" Reproduce random graph experiments from https://arxiv.org/pdf/2212.12812
    """

from ..generators.ising import generate_random_graph
from ._utils import do_ising_experiment
from ..wcnf.solvers import SOLVERS, SolverType

def run():
    """ Run all random graph Ising experiments and print results to console """
    results: dict[SolverType, list[tuple[int, float]]] = {}
    for solver_type in SOLVERS:
        results[solver_type] = []
        size = 50
        timed_out = False
        while not timed_out:
            model = generate_random_graph(size)
            cur = do_ising_experiment(f"Random graph size={size}; solver="
            f"{solver_type}", model, solver_type)
            if cur < 0.0:
                timed_out = True
            else:
                results[solver_type].append((size, cur))
            size += 20
    for solver_type, res in results.items():
        print(f"Results for solver {solver_type}:")
        print(" ".join(f"({r[0]}, {r[1]})" for r in res))