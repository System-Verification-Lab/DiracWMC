
from argparse import ArgumentParser

from ..wcnf.solver import SOLVERS, Solver
from ..generator.ising import generate_square_lattice
from ..converter import ising_to_wcnf

BETA = 1.0

parser = ArgumentParser(description="Reproduce square lattice experiments from "
"https://arxiv.org/pdf/2212.12812. Outputs a space-separated list of tuples "
"(size, runtime) (unless error calculation is enabled)")
parser.add_argument("sizes", type=str, help="A comma-separated list of lattice "
"sizes, or a string in the format start:stop:step where stop is not included")
parser.add_argument("-s", "--solver", type=str, choices=SOLVERS, default="dpmc",
help="The solver to use. Defaults to DPMC")
parser.add_argument("-t", "--timeout", type=float, default=15.0, help="The "
"timeout of the solver for each of the lattice sizes")
parser.add_argument("-e", "--measure-error", action="store_true", default=False,
help="Measure relative error instead of runtime and put this is output")
args = parser.parse_args()

if ":" in args.sizes:
    sizes = list(range(*(int(x) for x in args.sizes.split(":"))))
else:
    sizes = [int(x) for x in args.sizes.split(",")]
solver = Solver.from_solver_name(args.solver)
results: list[tuple[int, float]] = []
for size in sizes:
    model = generate_square_lattice(size)
    formula = ising_to_wcnf(model, BETA)
    result = solver.run_solver(formula)
    if not result.success:
        raise RuntimeError("Solver timed out")
    if args.measure_error:
        true_weight = model.partition_function(BETA)
        found_weight = result.total_weight
        error = abs(found_weight / true_weight - 1.0)
        results.append((size, error))
    else:
        results.append((size, result.runtime))
print(" ".join(f"({r[0]}, {r[1]})" for r in results))