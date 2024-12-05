
from src.models import IsingModel
from src.converters import ising_to_wcnf

model = IsingModel.from_string(open("examples/ising/two_spin.json").read())
print(model.partition_function(1.0))
wcnf = ising_to_wcnf(model, 1.0)
print(wcnf.total_weight())
print(wcnf.to_string())