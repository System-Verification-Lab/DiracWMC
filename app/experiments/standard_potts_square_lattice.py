
from argparse import ArgumentParser
from ..wcnf.solver import SOLVERS, Solver
from ..generator.potts import generate_standard_square_lattice
from ..converter import (potts_to_wcnf, standard_potts_to_potts,
standard_potts_to_wcnf)

BETA = 1.0

parser = ArgumentParser(description="Potts model square lattice experiments. "
"Outputs a space-separated list of tuples (size, runtime), unless error "
"calculation is enabled")
parser.add_argument("sizes", type=str, help="A comma-separated list of lattice "
"sizes, or a string in the format start:stop:step where stop is not included")
parser.add_argument("-s", "--solver", type=str, choices=SOLVERS, default="dpmc",
help="The solver to use. Defaults to DPMC")
parser.add_argument("-q", "--states", type=int, default=3, help="Number of "
"states every lattice site can have. Defaults to 3")
parser.add_argument("-t", "--timeout", type=float, default=15.0, help="The "
"timeout of the solver for each of the lattice sizes. Default is 15 seconds")
parser.add_argument("-m", "--method", type=str, choices=["direct", "indirect"],
default="direct", help="The method to use when converting a standard Potts "
"model to a weighted CNF formula")
parser.add_argument("-e", "--measure-error", action="store_true", default=False,
help="Measure relative error instead of runtime and put this is output")
args = parser.parse_args()

assert args.states >= 2
if ":" in args.sizes:
    sizes = list(range(*(int(x) for x in args.sizes.split(":"))))
else:
    sizes = [int(x) for x in args.sizes.split(",")]
solver = Solver.from_solver_name(args.solver, timeout=args.timeout)
results: list[tuple[int, float]] = []
for size in sizes:
    assert size >= 1
    model = generate_standard_square_lattice(size, args.states)
    if args.method == "direct":
        formula = standard_potts_to_wcnf(model, BETA)
    else:
        formula = potts_to_wcnf(standard_potts_to_potts(model), BETA)
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