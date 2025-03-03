
import random
from typing import Literal
from ...quantum_ising import QuantumIsingModel
from argparse import ArgumentParser

def generate_line(size: int, weights: Literal["normal", "signed"] = "normal", *,
ring: bool = False) -> QuantumIsingModel:
    """ Generate a line quantum Ising model with random weights. The weights
        can be initialized using a normal distribution or a distribution picking
        from -1 and +1 with equal probability """
    model = QuantumIsingModel(size)
    weight_func = {
        "normal": (lambda: random.normalvariate(0, 1)),
        "signed": (lambda: random.choice((-1, 1))),
    }[weights]
    for i in range(size if ring else size - 1):
        strength = weight_func()
        model[i, (i + 1) % size] = strength
    model.external_field_x = random.normalvariate()
    return model

if __name__ == "__main__":
    parser = ArgumentParser(description="Generate a line quantum Ising model "
    "with random weights and transverse field strength, given some number of "
    "spins")
    parser.add_argument("-n", "--spin-count", type=int, required=True, help=
    "Number of spins/nodes in the model")
    parser.add_argument("-w", "--weights", type=str, choices=["normal", "signed"
    ], default="normal", help="The probability distribution to use for the "
    "edge weights. Defaults to a normal distribution")
    parser.add_argument("-o", "--output", type=str, help="Output JSON file to "
    "write the quantum Ising model to. If no output file is given the output "
    "is printed to the console")
    parser.add_argument("-r", "--ring", action="store_true", help="Whether to "
    "connect the first and last spin in the line to create a ring",
    default=False)
    args = parser.parse_args()
    assert args.spin_count >= 2
    model = generate_line(args.spin_count, args.weights, ring=args.ring)
    model_string = model.to_string()
    if args.output:
        with open(args.output, "w") as f:
            f.write(model_string)
    else:
        print(model_string)