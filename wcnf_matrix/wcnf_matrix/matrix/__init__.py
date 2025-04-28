
from .abstractmatrix import ConcreteMatrix
from .labelmatrix import LabelMatrix
Matrix = ConcreteMatrix

bra = Matrix.bra
ket = Matrix.ket

def value[Field](matrix: Matrix[Field]) -> ConcreteMatrix[Field]:
    """ Convert matrix to a concrete matrix with actual values stored in memory
        """
    return matrix.value()