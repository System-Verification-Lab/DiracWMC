
from argparse import ArgumentParser
from .import quantum_ising_to_ising
from ...quantum_ising import QuantumIsingModel

parser = ArgumentParser(description="Approximate a quantum Ising model using a "
"classical ising model (the partition function of the classical model "
"approximates the quantum model). The input is JSON. The output is two lines: "
"The first line has the factor with which the partition function of the "
"classical model needs to be multiplied *per spin* to approximate the "
"partition function of the quantum model. The second line has a JSON "
"representation of the classical model")
parser.add_argument("filename", type=str, help="The path to the quantum Ising "
"model JSON file")
parser.add_argument("-o", "--output", type=str, help="The output file to store "
"the weighted CNF formula in. If not specified output will be dumped to the "
"console")
parser.add_argument("-b", "--beta", type=float, help="The inverse temperature "
"of the partition function. Defaults to 1.0", default=1.0)
parser.add_argument("-l", "--layers", type=int, help="Number of layers used in "
"the approximation. Defaults to 10", default=10)

args = parser.parse_args()

assert args.beta >= 0.0
assert args.layers >= 3

with open(args.filename, "r") as f:
    quantum_model = QuantumIsingModel.from_string(f.read())
ising_model, factor = quantum_ising_to_ising(quantum_model, args.beta,
args.layers)
output_string = ising_model.to_string()

if args.output:
    with open(args.output, "w") as f:
        f.write(f"{factor}\n{output_string}")
else:
    print(f"{factor}\n{output_string}")