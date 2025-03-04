
from time import time
from ..generators.quantum_ising import generate_ring

BETA = 1.0
SPINS_LIMIT = 12

def run():
    """ Run this experiment """
    # Calculate true value
    results: list[tuple[int, float]] = []
    for i in range(3, SPINS_LIMIT + 1):
        model = generate_ring(i)
        start = time()
        model.partition_function(BETA)
        results.append((i, time() - start))
    print()
    print("Results:")
    print(" ".join(f"({s},{r})" for s, r in results))
    print()