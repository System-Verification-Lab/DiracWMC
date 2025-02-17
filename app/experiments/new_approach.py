
from ..wcnf.solvers import DPMCSolver
from ..models import QuantumIsingModel
from ..converters import matrix_quantum_ising_to_wcnf
from time import time

SOLVER_TIMEOUT = 1.0
ERROR_THRESHOLD = 1e-13
FILENAME = "examples/quantum_ising/two_spin.json"
BETA = 1.0
TERMS_LIMIT = 30

def run():
    """ Run this experiment """
    content = open(FILENAME, "r").read()
    # Calculate true value
    model = QuantumIsingModel.from_string(content)
    true_weight = model.partition_function(BETA)
    print("True partition function:", true_weight)
    terms = 2
    timed_out = False
    results: dict[str, list[tuple[float, float]]] = {}
    while not timed_out:
        start = time()
        result = run_for_terms(model, terms, true_weight)
        end = time()
        if result is None:
            timed_out = True
        else:
            results.setdefault("total", []).append((result[0], end - start))
            results.setdefault("solver", []).append(result)
        terms += 1
        if terms > TERMS_LIMIT:
            break
    for name, result_list in results.items():
        print()
        print(f"Results {name}:")
        print(" ".join(f"({e},{r})" for e, r in result_list))
        print()

def run_for_terms(model: QuantumIsingModel, terms: int, true_weight: float) -> (
tuple[float, float] | None):
    """ Get the error and runtime of a certain number of terms approximation, or
        None if the run timed out or the error threshold is reached """
    wcnf = matrix_quantum_ising_to_wcnf(model, BETA, terms)
    solver = DPMCSolver(timeout=SOLVER_TIMEOUT)
    result = solver.run_solver(wcnf)
    print(f"Runtime for terms={terms}:", result.runtime, "s")
    if not result.success:
        print("Solver timed out")
        return None
    weight = result.total_weight
    error = abs(weight / true_weight - 1.0)
    if error < ERROR_THRESHOLD:
        print("Error threshold reached")
        return None
    print(f"Error for terms={terms}:", error)
    return (error, result.runtime)