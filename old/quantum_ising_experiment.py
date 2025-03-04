
import random
from typing import Iterable
from src.models import IsingModel, QuantumIsingModel
from src.converters import ising_to_wcnf, quantum_ising_to_ising
from src.wcnf import SolverInterface, SolverType, SOLVERS
from src.logger import ConsoleColor

def do_experiment(name: str, model: IsingModel, solver: SolverType, *, beta:
float = 1.0, target_weight: float | None = None) -> tuple[float, float]:
    """ Perform an experiment and display runtime, given the name of the
        experiment, the model, and the solver to use. Returns a tuple of
        (weight, runtime) """
    formula = ising_to_wcnf(model, beta)
    solver_interface = SolverInterface.from_solver_name(solver)
    weight = solver_interface.calculate_weight(formula)
    runtime = solver_interface.runtime
    print()
    print(f"{ConsoleColor.GREEN}Runtime of experiment \"{name}\": {runtime} "
    f"s{ConsoleColor.CLEAR}")
    if target_weight is not None:
        print(f"{ConsoleColor.GREEN}Error of experiment \"{name}\": "
        f"{abs(weight - target_weight)} s{ConsoleColor.CLEAR}")
    print()
    return (weight, runtime)

##########################################
# RING OF SPINS
##########################################

def all_ring_experiments(solver: SolverType, ring_size: int = 6) -> list[tuple[
float, float]]:
    """ Perform all ring spin experiments for a specific solver. Halts
        whenever a solver times out. The ring has a fixed size with beta=1. The
        number of layers of the approximation Ising model is varied. Returns
        tuples of the form (error, runtime). Traverse field strength is 1 """
    results: list[tuple[float, float]] = []
    layers = 3
    timed_out = False
    while not timed_out:
        try:
            quantum_model = QuantumIsingModel(ring_size, 1.0)
            for i in range(ring_size):
                strength = random.normalvariate(0, 1)
                quantum_model.add_interaction(i, (i + 1) % ring_size, strength)
            true_partition_func = quantum_model.partition_function(1.0)
            ising_model, factor = quantum_ising_to_ising(quantum_model, 1.0,
            layers)
            weight, runtime = do_experiment(f"Ring; Solver = {solver}; Layers "
            f"= {layers}", ising_model, solver)
            weight *= factor
            error = abs(weight - true_partition_func)
            results.append((error, runtime))
        except:
            timed_out = True
        layers += 1
    return results

results: dict[str, list[tuple[int, float]]] = {}
for solver in SOLVERS:
    results[f"Ring (size=6) {solver}"] = all_ring_experiments(solver)

for name, res in results.items():
    print(f"{name} results:")
    print(" ".join(f"({e}, {r})" for e, r in res))