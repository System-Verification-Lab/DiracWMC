
from .converter import ising_to_wcnf
from .ising_model import IsingModel

print(ising_to_wcnf(IsingModel(4)))