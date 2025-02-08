
from ..wcnf.solvers import SOLVERS, SolverType, Solver
from ..models import QuantumIsingModel
from ..converters import quantum_ising_to_wcnf
from ..logger import log_info, log_stat

def run():
    """ Run all quantum two spin experiments and print results to console """
    # solver name -> list[(error, runtime)]
    results: dict[SolverType, list[tuple[float, float]]] = {}
    quantum_model = QuantumIsingModel(2, interaction={(0, 1): 1.0},
    external_field_x=1.0)
    true_pf = quantum_model.partition_function(1.0)
    for solver_type in SOLVERS:
        results[solver_type] = []
        layers = 3
        timed_out = False
        while not timed_out:
            log_info(f"Running experiment for l={layers}")
            wcnf = quantum_ising_to_wcnf(quantum_model, 1.0, layers)
            solver = Solver.from_solver_name(solver_type)
            result = solver.run_solver(wcnf)
            if not result.success:
                timed_out = True
            else:
                est_pf = result.total_weight
                error = abs(est_pf / true_pf - 1.0)
                if error < 1e-5:
                    break
                log_stat(f"Partition function true for l={layers}", true_pf)
                log_stat(f"Partition function est. for l={layers}", est_pf)
                log_stat(f"Error for l={layers}; solver={solver_type}", error)
                results[solver_type].append((error, result.runtime))
            layers += 1
    for solver_type, res in results.items():
        print(f"Results for solver {solver_type}:")
        print(" ".join(f"({r[0]}, {r[1]})" for r in res))