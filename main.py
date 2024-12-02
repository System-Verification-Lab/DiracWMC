
from src.models import QuantumIsingModel

model = QuantumIsingModel.from_string(open("test.txt").read())
print(model.to_string())
print(model.hamiltonian())
print(model.partition_function())