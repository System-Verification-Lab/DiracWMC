
import random
from ...potts import PottsModel, StandardPottsModel
from argparse import ArgumentParser
from itertools import product

def generate_square_lattice(size: int, states: int) -> PottsModel:
    """ Generate a square lattice potts model with a random (normal)
        distribution of interaction strengths, where every pair of spin values
        is given an interaction strength. Arguments are the width/height of the
        lattice and the number of sites per lattice site """
    model = PottsModel(size * size, states)
    # Interactions
    def add_model_interaction(i: int, j: int):
        for si, sj in product(range(states), repeat=2):
            model[i, j, si, sj] = random.normalvariate(0, 1)
    for i in range(size * size):
        if i + size < size * size:
            add_model_interaction(i, i + size)
        if i % size != size - 1:
            add_model_interaction(i, i + 1)
    # External field strengths
    for i in range(size * size):
        for si in range(states):
            model[i, si] = random.normalvariate(0, 1)
    return model

def generate_standard_square_lattice(size: int, states: int) -> (
StandardPottsModel):
    """ Generate a square lattice standard potts model with a random (normal
        distribution) interaction strength. Arguments are the width/height of
        the lattice and the number of states one lattice site can have """
    model = StandardPottsModel(size * size, states, random.normalvariate(0, 1))
    for i in range(size * size):
        if i + size < size * size:
            model.add_interaction(i, i + size)
        if i % size != size - 1:
            model.add_interaction(i, i + 1)
    return model

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate a square lattice Potts model "
    "with random weights and external field strengths. Random values taken "
    "from normal distribution")
    parser.add_argument("-n", "--size", type=int, required=True, help="Width "
    "and height of the lattice")
    parser.add_argument("-q", "--states", type=int, required=True, help="The "
    "number of states every lattice site can have")
    parser.add_argument("-m", "--model-type", type=str, choices=("generalized",
    "standard"), default="generalized", help="Which type of Potts model to "
    "generate. Defaults to generalized Potts model")
    parser.add_argument("-o", "--output", type=str, help="Output JSON file to "
    "write the Potts model to. If no output file is given the output is "
    "printed to the console")
    args = parser.parse_args()
    assert args.size >= 2
    assert args.states >= 2
    if args.model_type == "generalized":
        model = generate_square_lattice(args.size, args.states)
    else:
        model = generate_standard_square_lattice(args.size, args.states)
    model_string = model.to_string()
    if args.output:
        with open(args.output, "w") as f:
            f.write(model_string)
    else:
        print(model_string)