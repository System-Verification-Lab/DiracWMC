
from src.models import IsingModel

model = IsingModel.from_string(open("examples/ising/two_spin.json").read())
print(model.to_string())
print(model.partition_function(1))