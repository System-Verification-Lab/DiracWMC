
from .abstractmatrix import AbstractMatrix
from ..index import Index, IndexBasisElement
from typing import Iterable, Self

class BasicMatrix[Field](AbstractMatrix[Field]):
    """ Basic matrix implementation using 2D lists """

    def __init__(self, index: Index[Field], values: Iterable[Iterable[Field]]):
        """ Initialize matrix using iterator over rows """
        super().__init__(index)
        self._values = list(list(row) for row in values)

    def __str__(self) -> str:
        """ String representation of the matrix """
        return "[ " + ", ".join(str(row) for row in self._values) + " ]"
    
    def __add__(self, other: Self) -> Self:
        values = []
        if len(self._values) != len(other._values):
            raise ValueError("Matrices don't have the same shape")
        for r1, r2 in zip(self._values, other._values):
            if len(r1) != len(r2):
                raise ValueError("Matrices don't have the same shape")
            values.append(a + b for a, b in zip(r1, r2))
        return BasicMatrix(self._index, values)

    @classmethod
    def bra(cls, element: IndexBasisElement[Field]) -> "BasicMatrix[Field]":
        zero, one = element.index.field(0), element.index.field(1)
        return BasicMatrix(element.index, [[one if i == element.element else
        zero for i in range(element.index.q)]])

    @classmethod
    def ket(cls, element: IndexBasisElement[Field]) -> "BasicMatrix[Field]":
        zero, one = element.index.field(0), element.index.field(1)
        return BasicMatrix(element.index, [[one] if i == element.element else
        [zero] for i in range(element.index.q)])