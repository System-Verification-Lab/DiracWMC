
from src.models import QuantumIsingModel
from src.converters import ising_to_wcnf, quantum_ising_to_ising
import sys
from pathlib import Path
from subprocess import Popen, PIPE
import os
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

class ConsoleColor:
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    GREY = "\033[90m"
    CLEAR = "\033[0m"

def run_dpmc(filename: str) -> float:
    """ Run the DPMC solver on the given .cnf file. Assumes that the DPMC solver
        is properly installed using `make solvers/DPMC`. Returns the total
        weight """
    cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "solvers",
    "DPMC")
    filepath = os.path.join(os.getcwd(), filename)
    infile = open(filepath, "r")
    p1 = Popen(["./lg/build/lg", "./lg/solvers/flow-cutter-pace17/"
    "flow_cutter_pace17 -p 100"], cwd=cwd, stdout=PIPE, stdin=infile)
    p2 = Popen(["./dmc/dmc", f"--cf={filepath}"], cwd=cwd, stdout=PIPE,
    stdin=p1.stdout)
    result = p2.stdout.read().decode("utf-8")
    for line in result.split("\n"):
        if line.startswith("c s exact double prec-sci"):
            return float(line.split()[-1])
    raise Exception("Could not find result of DPMC. Something must have gone "
    "wrong while running it")

def int_in_range(arg: str, mn: int | None = None, mx: int | None = None) -> int:
    """ Checks if the given argument is a string containing an integer that has
        the given minimum and/or maximum. None means there is no restriction """
    value = int(arg)
    if (mn is not None and mn > value) or (mx is not None and mx < value):
        raise ArgumentTypeError(f"{value} is in the range [{mn}, {mx}]")
    return value

parser = ArgumentParser(description="This program can be used to convert a "
"Quantum Ising Model file to a weighted CNF file using an approximation of the "
"Quantum Ising Model using a Classical Ising Model.")
parser.add_argument("filename", type=str, help="The source filename of the "
"Quantum Ising Model.")
parser.add_argument("-o", "--output", type=str, default="output.cnf", help=
"Output filename of the generated .cnf file. Must have a .cnf extension. "
"Defaults to output.cnf")
parser.add_argument("-s", "--solver", type=str, choices=["DPMC"], help="Solver "
"to use to determine weight of generated wCNF formula. If omitted, no solver "
"is used and weight is not determined.")
parser.add_argument("-i", "--ising", action="store_true", help="Generate a "
"file with the Classical Ising Model approximation of the Quantum Ising Model. "
"The file will be in the same location and have the same name as the output, "
"but has a .json extension")
parser.add_argument("-b", "--beta", type=float, default=1.0, help="Inverse "
"temperature of the Quantum Ising Model. Defaults to 1.")
parser.add_argument("-l", "--layers", type=lambda x: int_in_range(x, 3),
default=10, help="Number of layers the Classical Ising Model uses to "
"approximate the Quantum Ising Model.")
parser.add_argument("-d", "--debug", action="count", help="Enables debugging "
"information based on number of times argument is repeated: Once for exact "
"calculation of partition function, twice for determining partition function "
"of classical model, as well as the total weight of the wCNF formula, using "
"brute force", default=0)
args = parser.parse_args()

print()
print(f"{ConsoleColor.CYAN}Input filename:{ConsoleColor.CLEAR} {args.filename}")
print(f"{ConsoleColor.CYAN}Inverse temperature:{ConsoleColor.CLEAR} "
f"{args.beta}")
print(f"{ConsoleColor.CYAN}Approximation layers:{ConsoleColor.CLEAR} "
f"{args.layers}")
print()

print(f"{ConsoleColor.GREY}Reading input file...{ConsoleColor.CLEAR}")
with open(args.filename) as input_file:
    quantum_model = QuantumIsingModel.from_string(input_file.read())

print(f"{ConsoleColor.GREY}Converting to Classical Ising Model..."
f"{ConsoleColor.CLEAR}")
model, factor = quantum_ising_to_ising(quantum_model, args.beta, args.layers)

if args.ising:
    ising_filename = str(Path(args.output).with_suffix(".json"))
    print(f"{ConsoleColor.GREY}Writing to output file {ising_filename}..."
    f"{ConsoleColor.CLEAR}")
    with open(ising_filename, "w") as ising_file:
        ising_file.write(str(model))

print(f"{ConsoleColor.GREY}Converting to wCNF formula...{ConsoleColor.CLEAR}")
wcnf = ising_to_wcnf(model, 1.0)

print(f"{ConsoleColor.GREY}Writing to output file {args.output}..."
f"{ConsoleColor.CLEAR}")
with open(args.output, "w") as output_file:
    output_file.write(str(wcnf))

solver_output: float | None = None
match args.solver:
    case "DPMC": solver_output = run_dpmc(args.output)
    case None: pass
    case _: raise Exception(f"Solver {args.solver} unimplemented")

print()
if solver_output is not None:
    print(f"{ConsoleColor.CYAN}Solver output:{ConsoleColor.CLEAR} "
    f"{solver_output}")
if args.debug >= 2:
    classical_partition = model.partition_function(1.0)
    print(f"{ConsoleColor.CYAN}Classical model partition function:"
    f"{ConsoleColor.CLEAR} {classical_partition}")
    wcnf_weight = wcnf.total_weight()
    print(f"{ConsoleColor.CYAN}Weight of wCNF formula:{ConsoleColor.CLEAR} "
    f"{classical_partition}")
print(f"{ConsoleColor.CYAN}Multiplication factor:{ConsoleColor.CLEAR} "
f"{factor}")
if solver_output is not None:
    quantum_partition_est = solver_output * factor
    print(f"{ConsoleColor.CYAN}Quantum model partition function (estimate):"
    f"{ConsoleColor.CLEAR} {quantum_partition_est}")
if args.debug >= 1:
    quantum_partition = quantum_model.partition_function(args.beta)
    print(f"{ConsoleColor.CYAN}Quantum model partition function (exact):"
    f"{ConsoleColor.CLEAR} {quantum_partition}")
print()