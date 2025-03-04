
import random
from typing import Literal
from ...ising import IsingModel
from argparse import ArgumentParser

def generate_random_graph(size: int, degree: int = 3, weights: Literal["normal",
"signed"] = "normal"):
    """ Generate a random regular graph with vertices with the given degree. The
        interaction weights are generated according to the distribution given
        (by default normal(0, 1), but a sample from +-1 is also possible).
        External field strengths are set independently per vertex to a value
        sampled from normal(0, 1). Throws an error if size*degree is not even
        """
    model = IsingModel(size)
    weight_func = {
        "normal": lambda: random.normalvariate(0, 1),
        "signed": lambda: random.choice((-1, 1)),
    }[weights]
    assert size * degree % 2 == 0
    nodes = sum(([i] * degree for i in range(size)), [])
    random.shuffle(nodes)
    for i, j in zip(nodes[::2], nodes[1::2]):
        model[i, j] = weight_func()
    # External field strengths
    for i in range(size):
        model[i] = random.normalvariate(0, 1)
    return model

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate a random graph Ising model "
    "with random weights and external field strengths, given some degree. It "
    "is required that spin-count * degree is divisible by 2!")
    parser.add_argument("-n", "--spin-count", type=int, required=True, help=
    "Number of spins/nodes in the random graph")
    parser.add_argument("-d", "--degree", type=int, default=3, help="Degree of "
    "each node in the random graph")
    parser.add_argument("-w", "--weights", type=str, choices=["normal",
    "signed"], default="normal", help="The probability distribution to use for "
    "the edge weights. Defaults to a normal distribution")
    parser.add_argument("-o", "--output", type=str, help="Output JSON file to "
    "write the Ising model to. If no output file is given the output is "
    "printed to the console")
    args = parser.parse_args()
    assert args.spin_count >= 2
    assert args.degree >= 1
    model = generate_random_graph(args.spin_count, args.degree, args.weights)
    model_string = model.to_string()
    if args.output:
        with open(args.output, "w") as f:
            f.write(model_string)
    else:
        print(model_string)