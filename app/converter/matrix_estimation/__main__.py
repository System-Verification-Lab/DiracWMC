
from argparse import ArgumentParser
from . import matrix_quantum_ising_to_wcnf
from ...quantum_ising import QuantumIsingModel

parser = ArgumentParser(description="Approximate a quantum Ising model given as "
"JSON using a weighted CNF formula (also stored as JSON), such that the "
"partition function of the quantum Ising model is approximately the same as "
"the total weight of the formula. This uses a direct method approximating the "
"Taylor series of the matrix exponential")
parser.add_argument("filename", type=str, help="The path to the quantum Ising "
"model JSON")
parser.add_argument("-o", "--output", type=str, help="The output file to store "
"the CNF formula in. If not specified output will be dumped to the console")
parser.add_argument("-b", "--beta", type=float, help="The inverse temperature "
"of the partition function. Defaults to 1.0", default=1.0)
parser.add_argument("-k", "--approx-terms", type=int, help="The number of "
"terms to use to approximate the Taylor series of the parition function. "
"Defaults to 4", default=4)

args = parser.parse_args()

with open(args.filename, "r") as f:
    quantum_model = QuantumIsingModel.from_string(f.read())
output_string = matrix_quantum_ising_to_wcnf(quantum_model, args.beta,
args.approx_terms).to_string()

if args.output:
    with open(args.output, "w") as f:
        f.write(output_string)
else:
    print(output_string)
