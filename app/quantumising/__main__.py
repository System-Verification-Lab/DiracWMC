
from argparse import ArgumentParser
from . import QuantumIsingModel

parser = ArgumentParser(description="Parse a quantum Ising model JSON file. "
"Optionally the Hamiltonian and partition function can be calculated")
parser.add_argument("filename", type=str, help="Filename of the quantum Ising "
"model JSON file")
parser.add_argument("-H", "--hamiltonian", action="store_true", help=
"Calculate and display the Hamiltonian associated with the quantum Ising model")
parser.add_argument("-p", "--partition-func", action="store_true", help=
"Calculate the partition function of the Ising model using brute force")
parser.add_argument("-b", "--beta", type=float, help="The inverse temperature "
"in case the partition function is calculated (see -p). If the partition "
"function is not calculated this has no effect. Defaults to 1.0")

args = parser.parse_args()
with open(args.filename, "r") as f:
    model = QuantumIsingModel.from_string(f.read())
print(model)
if args.hamiltonian:
    h = model.hamiltonian()
    print()
    print(f"Hamiltonian:\n{h}")
if args.partition_func:
    beta = args.beta if args.beta else 1.0
    pf = model.partition_function(beta)
    print()
    print(f"Partition function: {pf:.12f}")
