
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Self, Any, Iterable, TYPE_CHECKING
from ..index import Index, IndexBasisElement
from ..reg import Reg
# To prevent circular imports at runtime:
if TYPE_CHECKING:
    from .concretematrix import ConcreteMatrix
    from .labelmatrix import LabelMatrix

class AbstractMatrix[Field](ABC):
    """ Abstract definition of a matrix, with operations for creating bras and
        kets, addition, multiplication, etc. """
    
    def __init__(self, index: Index[Field]):
        """ Constructor with the Hilbert space the matrix operates on """
        self._index = index

    def __add__(self, other: Self) -> Self:
        """ Add two matrices together and return the result """
        return self.__class__.linear_comb(self, other)

    def __sub__(self, other: Self) -> Self:
        """ Subtract one matrix from another and return the result """
        return self.__class__.linear_comb(self, (self._index.field(-1), other))

    def __mul__(self, other: Self | Field) -> Self:
        """ Multiply two matrices (other being on the right), or multiply the
            matrix with a scalar value """
        if isinstance(other, self.__class__):
            return self.__class__.product(self, other)
        return self.__class__.linear_comb((self._index.field(other), self))

    def __rmul__(self, other: Field) -> Self:
        """ Multiply this matrix with a scalar value on the left """
        return self.__class__.linear_comb((self._index.field(other), self))

    def __pow__(self, other: Self) -> Self:
        """ Return the Kronecker product of this matrix and another """
        return self.__class__.kron(self, other)

    def __or__(self, other: Reg | Iterable[Reg]) -> LabelMatrix[Field, Self]:
        """ Alias of the label member function, which creates a LabelMatrix
            from this matrix. The original matrix is not modified """
        if isinstance(other, Reg):
            return self.label((other,))
        return self.label(other)

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """ Returns if this matrix is equal to another object. Comparing to any
            non-matrix object returns False """
        pass

    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]:
        """ The dimensions of the matrix as a tuple (rows, columns) """
        pass

    @classmethod
    @abstractmethod
    def bra(cls, *elements: IndexBasisElement[Field]) -> Self:
        """ Row vector of one or more basis elements in the Hilbert space """
        pass

    @classmethod
    @abstractmethod
    def ket(cls, *elements: IndexBasisElement[Field]) -> Self:
        """ Column vector of one or more basis elements in the Hilbert space """
        pass

    @classmethod
    @abstractmethod
    def linear_comb(cls, *elements: tuple[Field, Self] | Self) -> Self:
        """ Returns a linear combination of matrices, where each element can be
            a tuple (factor, matrix) or just a matrix, which is equivalent to
            (1, matrix) """
        pass

    @classmethod
    @abstractmethod
    def product(cls, *elements: Self) -> Self:
        """ Returns the product of matrices given from left to right """
        pass

    @classmethod
    @abstractmethod
    def kron(cls, *elements: Self) -> Self:
        """ Returns the kronecker product of zero or more matrices. In the case
            of zero matrices the 1x1 identity matrix is returned """
        pass

    @abstractmethod
    def value(self) -> ConcreteMatrix[Field]:
        """ Convert the matrix to a concrete matrix with actual values stored in
            memory """
        pass

    @abstractmethod
    def permutation(self, src_indices: Iterable[int], dst_indices: Iterable[int]
    | None = None) -> Self:
        """ Permute the input and output Hilbert subspaces given by the
            permutations src_indices and dst_indices respectively. Each is an
            iterable over indices from the original Hilbert subspaces. The
            matrix dimensions should be powers of q, otherwise a RuntimeError
            is thrown. If dst_indices is not given, it is set to be equal to
            src_indices. If any of the values from src_indices or dst_indices
            are out of range, a ValueError is thrown.
             
            In addition to indices of the original Hilbert subspaces, -1 can be
            used for a new Hilbert subspace with the identity operator acting on
            it. The number of -1 entries in src_indices and dst_indices should
            be the same. A ValueError is thrown if this is not the case """
        pass

    @abstractmethod
    def copy(self) -> Self:
        """ Create a copy of the matrix and return this copy """
        pass

    def label(self, labels: Iterable[Reg]) -> LabelMatrix[Field, Self]:
        """ Create a LabelMatrix from this matrix using the given annotation.
            The iterator should yield a number of elements n, such that this
            matrix has dimensions q ** n. One of the dimensions (but not both!)
            can be 1, meaning the matrix is a row or column vector. The new
            LabelMatrix is returned, leaving the original matrix unmodified """
        from .labelmatrix import LabelMatrix
        return LabelMatrix(self.copy(), labels)
    
    @property
    def index(self) -> Index[Field]:
        """ The index (Hilbert space) of the matrix """
        return self._index

