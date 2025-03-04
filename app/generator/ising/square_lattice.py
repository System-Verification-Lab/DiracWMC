
import random
from typing import Literal
from ...ising import IsingModel
from argparse import ArgumentParser

def generate_square_lattice(size: int, weights: Literal["normal", "signed"] =
"normal") -> IsingModel:
    """ Generate a square lattice Ising model with random weights. The weights
        can be initialized using a normal distribution or a distribution picking
        from -1 and +1 with equal probability """
    model = IsingModel(size * size)
    weight_func = {
        "normal": (lambda: random.normalvariate(0, 1)),
        "signed": (lambda: random.choice((-1, 1))),
    }[weights]
    # Interaction strengths
    for i in range(size * size):
        if i + size < size * size:
            strength = weight_func()
            model[i, i + size] = strength
        if i % size != size - 1:
            strength = weight_func()
            model[i, i + 1] = strength
    # External field strengths
    for i in range(size * size):
        model[i] = random.normalvariate(0, 1)
    return model

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate a square lattice Ising model "
    "with random weights and external field strengths")
    parser.add_argument("-n", "--size", type=int, required=True, help="Width "
    "and height of the lattice")
    parser.add_argument("-w", "--weights", type=str, choices=["normal",
    "signed"], default="normal", help="The probability distribution to use for "
    "the edge weights. Defaults to a normal distribution")
    parser.add_argument("-o", "--output", type=str, help="Output JSON file to "
    "write the Ising model to. If no output file is given the output is "
    "printed to the console")
    args = parser.parse_args()
    assert args.size >= 2
    model = generate_square_lattice(args.size, args.weights)
    model_string = model.to_string()
    if args.output:
        with open(args.output, "w") as f:
            f.write(model_string)
    else:
        print(model_string)