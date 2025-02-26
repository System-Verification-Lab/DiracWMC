
import json
import sys
import random
from datetime import datetime

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <spins>")
    print(f"Generates a ring with given number of spins")
    exit(1)
spins = int(sys.argv[1])
time_string = datetime.now().strftime("%Y%m%d_%H%M%S")
f = open(f"examples/quantum_ising/random_{spins}_{time_string}.json", "w")
f.write(json.dumps({
    "spin_count": spins,
    "external_field_x": random.normalvariate(),
    "interaction": [
        [i, (i + 1) % spins, random.normalvariate()]
        for i in range(spins)
    ],
}))