
import random
from ...potts import PottsModel, StandardPottsModel
from argparse import ArgumentParser
from itertools import product

def generate_random_graph(size: int, states: int, degree: int = 3):
    """ Generate a random regular graph with vertices with the given degree. The
        interaction weights are generated according to the normal distribution.
        External field strengths are set independently per vertex to a value
        sampled from normal(0, 1). Throws an error if size*degree is not even
        """
    model = PottsModel(size, states)
    assert size * degree % 2 == 0
    nodes = sum(([i] * degree for i in range(size)), [])
    random.shuffle(nodes)
    for i, j in zip(nodes[::2], nodes[1::2]):
        for si, sj in product(range(states), repeat=2):
            model[i, j, si, sj] = random.normalvariate()
    # External field strengths
    for i in range(size):
        for si in range(states):
            model[i, si] = random.normalvariate(0, 1)
    return model

def generate_standard_random_graph(size: int, states: int, degree: int):
    """ Generate a random regular graph with vertices with the given degree. The
        model is a standard Potts model on this graph, with interaction strength
        sampled from the normal distribution. Throws an error if size*degree is
        not even """
    model = StandardPottsModel(size, states, random.normalvariate())
    assert size * degree % 2 == 0
    nodes = sum(([i] * degree for i in range(size)), [])
    random.shuffle(nodes)
    for i, j in zip(nodes[::2], nodes[1::2]):
        model.add_interaction(i, j)
    return model

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate a random graph Potts model "
    "with random weights and external field strengths, given some degree. It "
    "is required that spin-count * degree is divisible by 2!")
    parser.add_argument("-n", "--size", type=int, required=True, help=
    "Number of nodes in the random graph")
    parser.add_argument("-q", "--states", type=int, required=True, help="The "
    "number of states every lattice site can have")
    parser.add_argument("-d", "--degree", type=int, default=3, help="Degree of "
    "each node in the random graph")
    parser.add_argument("-m", "--model-type", type=str, choices=("generalized",
    "standard"), default="generalized", help="Which type of Potts model to "
    "generate. Defaults to generalized Potts model")
    parser.add_argument("-o", "--output", type=str, help="Output JSON file to "
    "write the Ising model to. If no output file is given the output is "
    "printed to the console")
    args = parser.parse_args()
    assert args.spin_count >= 2
    assert args.degree >= 1
    if args.model_type == "generalized":
        model = generate_random_graph(args.size, args.states)
    else:
        model = generate_standard_random_graph(args.size, args.states)
    model_string = model.to_string()
    if args.output:
        with open(args.output, "w") as f:
            f.write(model_string)
    else:
        print(model_string)