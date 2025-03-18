
from argparse import ArgumentParser
from . import potts_to_wncf, standard_potts_to_potts, standard_potts_to_wcnf
from ...potts import PottsModel, StandardPottsModel

parser = ArgumentParser(description="Convert a Potts model given as JSON to a "
"weighted CNF formula (also stored as JSON), such that the partition function "
"of the Potts model is equal to the total weight of the formula")
parser.add_argument("filename", type=str, help="The path to the Potts model "
"JSON")
parser.add_argument("-o", "--output", type=str, help="The output file to store "
"the CNF formula in. If not specified output will be dumped to the console")
parser.add_argument("-b", "--beta", type=float, help="The constant to multiply "
"the Hamiltonian with in the partition function. Defaults to 1.0", default=1.0)
parser.add_argument("-f", "--format", type=str, choices=["generalized",
"standard"], default="generalized", help="The input format, which can be a "
"generalized or standard Potts model")
parser.add_argument("-m", "--method", type=str, choices=["direct", "indirect"],
default="direct", help="The method to use when converting a standard Potts "
"model. This has no effect for generalized Potts models")

args = parser.parse_args()

if args.format == "generalized":
    with open(args.filename, "r") as f:
        potts_model = PottsModel.from_string(f.read())
    output_string = potts_to_wncf(potts_model, args.beta).to_string()
    if args.output:
        with open(args.output, "w") as f:
            f.write(output_string)
    else:
        print(output_string)
else:
    with open(args.filename, "r") as f:
        potts_model = StandardPottsModel.from_string(f.read())
    if args.method == "direct":
        output_string = (standard_potts_to_wcnf(potts_model, args.beta)
        .to_string())
    else:
        output_string = potts_to_wncf(standard_potts_to_potts(potts_model),
        args.beta).to_string()
    if args.output:
        with open(args.output, "w") as f:
            f.write(output_string)
    else:
        print(output_string)
