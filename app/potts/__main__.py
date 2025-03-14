
from argparse import ArgumentParser
from . import PottsModel

parser = ArgumentParser(description="Parse a Potts model JSON file. Optionally "
"some information about the Potts model can be displayed")
parser.add_argument("filename", type=str, help="Filename of the Potts model "
"JSON file")
parser.add_argument("-p", "--partition-func", action="store_true", help=
"Calculate the partition function of the Potts model using brute force")
parser.add_argument("-b", "--beta", type=float, help="The constant factor beta "
"to put in front of the hamiltonian when the partition function is calculated "
"(see -p). If the partition function is not calculates this has no effect. "
"Defaults to 1.0")
args = parser.parse_args()
with open(args.filename, "r") as f:
    model = PottsModel.from_string(f.read())
print(model)
if args.partition_func:
    beta = 1.0 if not args.beta else args.beta
    pf = model.partition_function(beta)
    print()
    print(f"Partition function: {pf:.12f}")