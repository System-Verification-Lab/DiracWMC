
from argparse import ArgumentParser
from . import PottsModel
from . import StandardPottsModel

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
parser.add_argument("-v", "--variant", type=str, choices=("generalized",
"standard"), default="generalized", help="Which Potts model variant to read in "
"from the input file")
args = parser.parse_args()
with open(args.filename, "r") as f:
    match args.variant:
        case "generalized":
            model = PottsModel.from_string(f.read())
        case "standard":
            model = StandardPottsModel.from_string(f.read())
        case _:
            print(f"Invalid Potts model variant {args.variant}")
            exit(1)
print(model)
if args.partition_func:
    beta = 1.0 if not args.beta else args.beta
    pf = model.partition_function(beta)
    print()
    print(f"Partition function: {pf:.12f}")