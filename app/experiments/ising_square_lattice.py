
from ..models import IsingModel
from ..wcnf.solvers import SolverType, Solver
from ..converters import ising_to_wcnf
from ..logger import ConsoleColor

def do_experiment(name: str, model: IsingModel, solver: SolverType, *, beta:
float = 1.0) -> float:
    """ Perform an experiment and display runtime, given the name of the
        experiment, the model, and the solver to use. Returns the runtime """
    formula = ising_to_wcnf(model, beta)
    solver_interface = Solver.from_solver_name(solver)
    _ = solver_interface.calculate_weight(formula)
    runtime = solver_interface.runtime
    print()
    print(f"{ConsoleColor.GREEN}Runtime of experiment \"{name}\": {runtime} "
    f"s{ConsoleColor.CLEAR}")
    print()
    return runtime

def run():
    """ Run all square lattice Ising experiments """
    ...