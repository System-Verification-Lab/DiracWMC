
from argparse import ArgumentParser
from .formula import WCNF_FORMATS, WeightedCNFFormula

parser = ArgumentParser(description="Parses a JSON weighted CNF file and "
"optionally converts it to another format")
parser.add_argument("filename", type=str, help="Weighted CNF JSON file")
parser.add_argument("-o", "--output", type=str, help="Output file to store "
"weighted CNF formula, by default in JSON format. If this option is not "
"specified, dumps output to console")
parser.add_argument("-f", "--format", type=str, help="Format to use for the "
"output", default="json", choices=WCNF_FORMATS)

args = parser.parse_args()
with open(args.filename, "r") as f:
    formula = WeightedCNFFormula.from_string(f.read())
formula_string = formula.to_string(args.format)

if args.output:
    with open(args.output, "w") as f:
        f.write(formula_string)
else:
    print(formula_string)
