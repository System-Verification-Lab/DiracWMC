
from .ising_model import IsingModel
from wcnf_matrix import CNF, WeightFunction, BoolVar, WCNFMatrix

def ising_to_wcnf(model: IsingModel, beta: float = 1.0) -> tuple[CNF,
WeightFunction]:
    """ Convert the given Ising model to a CNF formula and weight function,
        such that the weighted model count of the formula w.r.t. the weight
        function is equal to the partition function of the Ising model at
        inverse temperature beta """
    ...

def ising_to_wcnf_matrix(model: IsingModel, beta: float = 1.0) -> WCNFMatrix:
    """ Convert the given Ising model to a WCNFMatrix, the trace of which is
        equal to the partition function of the Ising model at inverse
        temperature beta """
    ...