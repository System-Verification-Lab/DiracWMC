
from argparse import ArgumentParser
from . import potts_to_wncf
from ...potts import PottsModel

parser = ArgumentParser(description="Convert a Potts model given as JSON to a "
"weighted CNF formula (also stored as JSON), such that the partition function "
"of the Potts model is equal to the total weight of the formula")
parser.add_argument("filename", type=str, help="The path to the Potts model "
"JSON")
parser.add_argument("-o", "--output", type=str, help="The output file to store "
"the CNF formula in. If not specified output will be dumped to the console")
parser.add_argument("-b", "--beta", type=float, help="The constant to multiply "
"the Hamiltonian with in the partition function. Defaults to 1.0", default=1.0)

args = parser.parse_args()

with open(args.filename, "r") as f:
    potts_model = PottsModel.from_string(f.read())
output_string = potts_to_wncf(potts_model, args.beta).to_string()

if args.output:
    with open(args.output, "w") as f:
        f.write(output_string)
else:
    print(output_string)
