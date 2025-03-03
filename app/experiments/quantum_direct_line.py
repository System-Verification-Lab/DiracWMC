
from argparse import ArgumentParser

from ..wcnf.solver import SOLVERS, Solver
from ..generator.quantum_ising import generate_line
from ..converter import ising_to_wcnf, matrix_quantum_ising_to_wcnf

BETA = 1.0

parser = ArgumentParser(description="Experiment to approximate the quantum "
"Ising partition function using an approximation of the Taylor series of the "
"matrix exponential and converting it to a weighted CNF formula. Output is a "
"space-separated list of (error, runtime)")
parser.add_argument("spin_count", type=int, help="The number of spins in the "
"generated quantum models")
parser.add_argument("approx_terms", type=str, help="A comma-separated list of "
"approximation term counts, or a string in the format start:stop:step where "
"stop is not included in the tested spin-counts")
parser.add_argument("-s", "--solver", type=str, choices=SOLVERS, default="dpmc",
help="The solver to use. Defaults to DPMC")
parser.add_argument("-t", "--timeout", type=float, default=15.0, help="The "
"timeout in seconds of the solver for each of the lattice sizes. Defaults to 15"
)
parser.add_argument("-r", "--ring", action="store_true", default=False, help=
"Whether to use closed ring models instead of lines")
args = parser.parse_args()

if ":" in args.approx_terms:
    term_counts = list(range(*(int(x) for x in args.approx_terms.split(":"))))
else:
    term_counts = [int(x) for x in args.approx_terms.split(",")]
solver = Solver.from_solver_name(args.solver)
results: list[tuple[int, float]] = []
quantum_model = generate_line(args.spin_count, ring=args.ring)
print(quantum_model)
for terms in term_counts:
    formula = matrix_quantum_ising_to_wcnf(quantum_model, BETA,
    terms)
    result = solver.run_solver(formula)
    if not result.success:
        raise RuntimeError("Solver timed out")
    true_pf = quantum_model.partition_function(BETA)
    found_pf = result.total_weight
    error = abs(found_pf / true_pf - 1.0)
    results.append((error, result.runtime))
print(" ".join(f"({e}, {r})" for e, r in results))