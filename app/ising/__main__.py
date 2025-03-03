
from argparse import ArgumentParser
from . import IsingModel

parser = ArgumentParser(description="Parse an Ising model JSON file. "
"Optionally some information about the Ising model can be displayed")
parser.add_argument("filename", type=str, help="Filename of the Ising model "
"JSON file")
parser.add_argument("-p", "--partition-func", action="store_true", help=
"Calculate the partition function of the Ising model using brute force")
parser.add_argument("-b", "--beta", type=float, help="The inverse temperature "
"in case the partition function is calculated (see -p). If the partition "
"function is not calculated this has no effect")

args = parser.parse_args()
with open(args.filename, "r") as f:
    model = IsingModel.from_string(f.read())
print(model)
if args.partition_func:
    beta = 1.0 if not args.beta else args.beta
    pf = model.partition_function(beta)
    print()
    print(f"Partition function: {pf:.12f}")