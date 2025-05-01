
from .concretematrix import ConcreteMatrix
from .concretematrix import ConcreteMatrix as Matrix
from .labelmatrix import LabelMatrix

bra = Matrix.bra
ket = Matrix.ket

def value[Field](matrix: Matrix[Field]) -> ConcreteMatrix[Field]:
    """ Convert matrix to a concrete matrix with actual values stored in memory
        """
    return matrix.value()