
from .abstractmatrix import AbstractMatrix
from .concretematrix import ConcreteMatrix
from .labelmatrix import LabelMatrix
from typing import overload

type Matrix[Field] = ConcreteMatrix[Field]

bra = Matrix.bra
ket = Matrix.ket

@overload
def value[Field, MatrixType: AbstractMatrix[Field]](matrix: LabelMatrix[Field,
MatrixType]) -> LabelMatrix[Field, ConcreteMatrix[Field]]:
    """ Convert any LabelMatrix to a LabelMatrix using concrete values stored in
        memory, instead of some other representation """
    ...

@overload
def value[Field](matrix: Matrix[Field]) -> ConcreteMatrix[Field]:
    """ Convert a matrix to a concrete matrix with actual values stored in
        memory """
    ...

def value(matrix):
    """ Convert matrix to a concrete matrix with actual values stored in memory
        """
    return matrix.value()