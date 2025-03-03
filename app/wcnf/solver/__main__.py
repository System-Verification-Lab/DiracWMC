
from argparse import ArgumentParser
from ..formula import WeightedCNFFormula
from . import Solver, SOLVERS

parser = ArgumentParser(description="Runs a solver on the given weighted CNF "
"JSON file")
parser.add_argument("filename", type=str, help="Weighted CNF JSON file")
parser.add_argument("-s", "--solver", type=str, help="The solver to run",
default="dpmc", choices=SOLVERS)

args = parser.parse_args()
with open(args.filename, "r") as f:
    formula = WeightedCNFFormula.from_string(f.read())
solver = Solver.from_solver_name(args.solver)
result = solver.run_solver(formula)
print(result)