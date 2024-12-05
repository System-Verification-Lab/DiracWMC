
from src.models import IsingModel
from src.converters import ising_to_wcnf

model = IsingModel.from_string(open("examples/ising/two_spin.json").read())
wcnf = ising_to_wcnf(model, 1.0)
print(wcnf.to_string())