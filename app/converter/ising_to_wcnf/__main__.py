
from argparse import ArgumentParser
from . import ising_to_wcnf
from ...ising import IsingModel

parser = ArgumentParser(description="Convert an Ising model given as JSON to a "
"weighted CNF formula (also stored as JSON), such that the partition function "
"of the Ising model is equal to the total weight of the formula")
parser.add_argument("filename", type=str, help="The path to the Ising model "
"JSON")
parser.add_argument("-o", "--output", type=str, help="The output file to store "
"the CNF formula in. If not specified output will be dumped to the console")
parser.add_argument("-b", "--beta", type=float, help="The inverse temperature "
"of the partition function. Defaults to 1.0", default=1.0)

args = parser.parse_args()

with open(args.filename, "r") as f:
    ising_model = IsingModel.from_string(f.read())
output_string = ising_to_wcnf(ising_model, args.beta).to_string()

if args.output:
    with open(args.output, "w") as f:
        f.write(output_string)
else:
    print(output_string)
