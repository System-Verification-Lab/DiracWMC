
from .abstractmatrix import AbstractMatrix
from ..index import Index, IndexBasisElement
from typing import Iterable, Self, Any
from itertools import product
from functools import reduce

class ConcreteMatrix[Field](AbstractMatrix[Field]):
    """ Basic matrix implementation using 2D lists """

    def __init__(self, index: Index[Field], values: Iterable[Iterable[Field]]):
        """ Initialize matrix using iterator over rows """
        super().__init__(index)
        self._values = list(list(row) for row in values)

    def __str__(self) -> str:
        """ String representation of the matrix """
        return "[ " + ", ".join(str(row) for row in self._values) + " ]"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if self._index != other._index:
            return False
        if self.shape != other.shape:
            return False
        return all(all(a == b for a, b in zip(row_a, row_b)) for row_a, row_b in
        zip(self._values, other._values))

    @classmethod
    def bra[Field](cls, *elements: IndexBasisElement[Field]) -> (
    "ConcreteMatrix[Field]"):
        if len(elements) == 0:
            raise ValueError("Cannot construct bra from zero basis elements")
        if not all(elt.index == elements[0].index for elt in elements):
            raise ValueError("Cannot construct bra from basis elements from "
            "different fields")
        q, index = elements[0].index.q, elements[0].index
        zero, one = elements[0].index.field(0), elements[0].index.field(1)
        true_index = sum(elt.value * q ** i for i, elt in enumerate(
        reversed(elements)))
        return ConcreteMatrix(index, [[one if i == true_index else zero for i in
        range(q ** len(elements))]])

    @classmethod
    def ket[Field](cls, *elements: IndexBasisElement[Field]) -> (
    "ConcreteMatrix[Field]"):
        if len(elements) == 0:
            raise ValueError("Cannot construct ket from zero basis elements")
        if not all(elt.index == elements[0].index for elt in elements):
            raise ValueError("Cannot construct ket from basis elements from "
            "different fields")
        q, index = elements[0].index.q, elements[0].index
        zero, one = elements[0].index.field(0), elements[0].index.field(1)
        true_index = sum(elt.value * q ** i for i, elt in enumerate(
        reversed(elements)))
        return ConcreteMatrix(index, [[one if i == true_index else zero] for i
        in range(q ** len(elements))])
    
    @classmethod
    def linear_comb[Field](cls, *elements: """tuple[Field, ConcreteMatrix[Field]
    ] | ConcreteMatrix[Field]""") -> "ConcreteMatrix[Field]":
        if len(elements) == 0:
            raise ValueError("Cannot determine linear combination of zero "
            "matrices")
        if isinstance(elements[0], ConcreteMatrix):
            one = elements[0]._index.field(1)
        else:
            one = elements[0][1]._index.field(1)
        elements = tuple(elt if isinstance(elt, tuple) else (one, elt) for elt
        in elements)
        if not all(elt[1].shape == elements[0][1].shape for elt in elements):
            raise ValueError("Not all matrices in linear combination have the "
            "same shape")
        if not all(elt[1]._index == elements[0][1]._index for elt in elements):
            raise ValueError("Cannot calculate linear combination of matrices "
            "with different index")
        index = elements[0][1]._index
        zero = elements[0][1]._index.field(0)
        shape = elements[0][1].shape
        values = [[zero for _ in range(shape[1])] for _ in range(shape[0])]
        for factor, elt in elements:
            for i, j in product(range(shape[0]), range(shape[1])):
                values[i][j] += factor * elt._values[i][j]
        return ConcreteMatrix(index, values)

    @classmethod
    def product[Field](cls, *elements: "ConcreteMatrix[Field]") -> (
    "ConcreteMatrix[Field]"):
        if not all(elt._index == elements[0]._index for elt in elements):
            raise ValueError("Cannot calculate product of matrices with "
            "different index")
        return reduce(cls._multiply_matrices, elements)

    @classmethod
    def kron[Field](cls, *elements: "ConcreteMatrix[Field]") -> (
    "ConcreteMatrix[Field]"):
        if not all(elt._index == elements[0]._index for elt in elements):
            raise ValueError("Cannot calculate product of matrices with "
            "different index")
        return reduce(cls._kron_matrices, elements)

    @property
    def shape(self) -> tuple[int, int]:
        """ The shape of the matrix as a tuple (rows, columns) """
        return (len(self._values), len(self._values[0]))

    @classmethod
    def _multiply_matrices[Field](cls, left: "ConcreteMatrix[Field]", right:
    "ConcreteMatrix[Field]") -> "ConcreteMatrix[Field]":
        """ Multiply two matrices and return the result. Assumes matrices have
            the same index """
        if left.shape[1] != right.shape[0]:
            raise ValueError(f"Cannot multiply matrices with incompatible "
            f"shapes {left.shape} and {right.shape}")
        zero = left._index.field(0)
        values = [[zero for _ in range(right.shape[1])] for _ in range(
        left.shape[0])]
        for i, j in product(range(left.shape[0]), range(right.shape[1])):
            for k in range(left.shape[1]):
                values[i][j] += left._values[i][k] * right._values[k][j]
        return ConcreteMatrix(left._index, values)
    
    @classmethod
    def _kron_matrices[Field](cls, left: "ConcreteMatrix[Field]", right:
    "ConcreteMatrix[Field]") -> "ConcreteMatrix[Field]":
        """ Compute the kronecker product of two matrices and return the result.
            Assumes matrices have the same index """
        zero = left._index.field(0)
        values = [[zero for _ in range(left.shape[1] * right.shape[1])] for _ in
        range(left.shape[0] * right.shape[1])]
        for left_i, right_i, left_j, right_j in product(range(left.shape[0]),
        range(right.shape[0]), range(left.shape[0]), range(right.shape[1])):
            values[left_i * right.shape[0] + right_i][left_j * right.shape[1] +
            right_j] = left._values[left_i][left_j] * right._values[right_i][
            right_j]
        return ConcreteMatrix(left._index, values)