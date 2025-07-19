
from argparse import ArgumentParser
from ..wcnf.solver import SOLVERS, Solver
from ..generator.potts import (generate_standard_square_lattice,
generate_standard_random_graph)
from ..converter import (potts_to_wcnf, standard_potts_to_potts,
standard_potts_to_wcnf)

BETA = 1.0

parser = ArgumentParser(description="Potts model experiments. Outputs a "
"space-separated list of tuples (size, runtime), unless error calculation is "
"enabled")
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
parser.add_argument("-x", "--run-until-timeout", action="store_true", default=
False, help="When present, a timeout results in the result thus far being "
"displayed instead of an error")
parser.add_argument("-g", "--graph-type", type=str, choices=["square_lattice",
"random_graph"], default="square_lattice", help="Graph type to perform "
"experiments on. Random graphs are regular with degree 4")
parser.add_argument("-r", "--repeats", type=int, default=1, help="Number of "
"times to repeat an experiment and average results over. Defaults to 1")
args = parser.parse_args()

assert args.states >= 2
assert args.repeats >= 1
if ":" in args.sizes:
    sizes = list(range(*(int(x) for x in args.sizes.split(":"))))
else:
    sizes = [int(x) for x in args.sizes.split(",")]
solver = Solver.from_solver_name(args.solver, timeout=args.timeout)
results: list[tuple[int, float]] = []
timed_out = False
for size in sizes:
    assert size >= 1
    total = 0.0
    for _ in range(args.repeats):
        if args.graph_type == "square_lattice":
            model = generate_standard_square_lattice(size, args.states)
        else:
            model = generate_standard_random_graph(size, args.states, 4)
        if args.method == "direct":
            formula = standard_potts_to_wcnf(model, BETA)
        else:
            formula = potts_to_wcnf(standard_potts_to_potts(model), BETA)
        result = solver.run_solver(formula)
        if not result.success:
            if args.run_until_timeout:
                print("Solver timed out")
                timed_out = True
                break
            else:
                raise RuntimeError("Solver timed out")
        if args.measure_error:
            true_weight = model.partition_function(BETA)
            found_weight = result.total_weight
            error = abs(found_weight / true_weight - 1.0)
            total += error
        else:
            total += result.runtime
    if timed_out:
        break
    results.append((size, total / args.repeats))
print(" ".join(f"({r[0]}, {r[1]})" for r in results))