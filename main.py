
from src.models import QuantumIsingModel
from src.converters import ising_to_wcnf, quantum_ising_to_ising
import sys
from pathlib import Path

if len(sys.argv) not in (2, 3):
    print(f"Usage: {sys.argv[0]} <filename> [inverse_temperature]")
    exit(1)

input_file = sys.argv[1]
output_file = str(Path(sys.argv[1]).with_suffix(".cnf"))
beta = 1.0 if len(sys.argv) <= 2 else float(sys.argv[2])

quantum_model = QuantumIsingModel.from_string(open(input_file).read())
model, factor = quantum_ising_to_ising(quantum_model, beta, 50)
wcnf = ising_to_wcnf(model, 1.0)
open(output_file, "w").write(str(wcnf))

print(quantum_model.partition_function(beta))
print(factor)
# print(model.partition_function(1.0) * factor)
# print(wcnf.total_weight() * factor)