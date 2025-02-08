
from ..models import IsingModel
from ..wcnf.solvers import SolverType, Solver
from ..converters import ising_to_wcnf
from ..logger import ConsoleColor, log_warning

def do_ising_experiment(name: str, model: IsingModel, solver_type: SolverType,
*, beta: float = 1.0, verify_result: None | float = None) -> float:
    """ Perform an experiment and display runtime, given the name of the
        experiment, the model, and the solver to use. Returns the runtime, or -1
        if the experiment has a timeout """
    formula = ising_to_wcnf(model, beta)
    solver = Solver.from_solver_name(solver_type)
    result = solver.run_solver(formula)
    if not result.success:
        return -1.0
    runtime = result.runtime
    if verify_result is not None:
        weight = result.total_weight
        true_weight = model.partition_function()
        error = weight / true_weight - 1
        if error > verify_result:
            log_warning(f"Result of Ising model is incorrect for solver "
            f"{solver_type} (error {error})")
            return -1.0
    print()
    print(f"{ConsoleColor.GREEN}Runtime of experiment \"{name}\": {runtime} "
    f"s{ConsoleColor.CLEAR}")
    print()
    return runtime