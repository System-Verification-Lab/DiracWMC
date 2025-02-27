
from ..wcnf.solvers import DPMCSolver
from ..models import QuantumIsingModel
from ..converters import matrix_quantum_ising_to_wcnf
from ..generators.quantum_ising import generate_ring
from time import time

ERROR_THRESHOLD = 1e-2
BETA = 1.0
SOLVER_TIMEOUT = 30.0
SPINS_LIMIT = 5

def run():
    """ Run this experiment """
    # List of (qubits, runtime)
    results: dict[str, list[tuple[int, float]]] = {
        "solver": [],
        "direct": [],
    }
    for i in range(1, SPINS_LIMIT + 1):
        model = generate_ring(i, line=True)
        # Measure true partition function
        start = time()
        true_weight = model.partition_function(BETA)
        true_runtime = time() - start
        error, runtime = float("inf"), 0.0
        terms = 2
        while error > ERROR_THRESHOLD:
            print("qubits =", i, "terms =", terms)
            cur = run_for_terms(model, terms, true_weight)
            if cur is None:
                raise RuntimeError("Timeout")
            error, runtime = cur
            terms += 1
        results["solver"].append((i, runtime))
        results["direct"].append((i, true_runtime))
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
    print(f"Error for terms={terms}:", error)
    return (error, result.runtime)