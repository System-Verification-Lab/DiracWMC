
from __future__ import annotations
from typing import Iterable, Any, Self
from itertools import product
from functools import reduce
from ..index import Index, IndexBasisElement
from .abstractmatrix import AbstractMatrix

class ConcreteMatrix[Field](AbstractMatrix[Field]):
    """ Basic matrix implementation using 2D lists """

    def __init__(self, index: Index[Field], values: Iterable[Iterable[Field]]):
        """ Initialize matrix using iterator over rows """
        super().__init__(index)
        self._values = list(list(row) for row in values)

    def __str__(self) -> str:
        """ String representation of the matrix """
        entries = [[str(cell) for cell in row] for row in self._values]
        max_len = max(max(len(cell) for cell in row) for row in entries)
        return "[ " + "\n  ".join("  ".join(cell.rjust(max_len) for cell in row)
        for row in entries) + " ]"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if self._index != other._index:
            return False
        if self.shape != other.shape:
            return False
        return all(all(a == b for a, b in zip(row_a, row_b)) for row_a, row_b in
        zip(self._values, other._values))

    def __getitem__(self, key: tuple[int, int]) -> Field:
        """ Get an entry from the matrix given by (row, column) """
        return self._values[key[0]][key[1]]
    
    def __setitem__(self, key: tuple[int, int], value: Field):
        """ Set an entry in the matrix at position (row, column) to the given
            value """
        self._values[key[0]][key[1]] = value

    @classmethod
    def zeros[Field](cls, index: Index[Field], shape: tuple[int, int]) -> (
    ConcreteMatrix[Field]):
        """ Get a concrete matrix with the given dimensions, filled with zeros
            """
        return ConcreteMatrix(index, ((0 for _ in range(shape[1])) for _ in
        range(shape[0])))

    @classmethod
    def bra[Field](cls, *elements: IndexBasisElement[Field]) -> ConcreteMatrix[
    Field]:
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
    def ket[Field](cls, *elements: IndexBasisElement[Field]) -> ConcreteMatrix[
    Field]:
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
    def identity[Field](cls, index: Index[Field], size: int) -> ConcreteMatrix[
    Field]:
        zero, one = index.field(0), index.field(1)
        q = index.q
        return ConcreteMatrix(index, [[one if i == j else zero for j in
        range(q ** size)] for i in range(q ** size)])

    @classmethod
    def linear_comb[Field](cls, *elements: tuple[Field, ConcreteMatrix[Field]] |
    ConcreteMatrix[Field]) -> ConcreteMatrix[Field]:
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
    def product[Field](cls, *elements: ConcreteMatrix[Field]) -> ConcreteMatrix[
    Field]:
        if not all(elt._index == elements[0]._index for elt in elements):
            raise ValueError("Cannot calculate product of matrices with "
            "different index")
        return reduce(cls._multiply_matrices, elements)

    @classmethod
    def kron[Field](cls, *elements: ConcreteMatrix[Field]) -> ConcreteMatrix[
    Field]:
        if not all(elt._index == elements[0]._index for elt in elements):
            raise ValueError("Cannot calculate product of matrices with "
            "different index")
        return reduce(cls._kron_matrices, elements)

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self._values), len(self._values[0]))
    
    def copy(self) -> ConcreteMatrix[Field]:
        return ConcreteMatrix(self._index, self._values)

    def value(self) -> ConcreteMatrix[Field]:
        return self.copy()

    def permutation(self, src_indices: Iterable[int], dst_indices: Iterable[int]
    | None = None) -> Self:
        src_indices = list(src_indices)
        dst_indices = src_indices if dst_indices is None else list(dst_indices)
        log_shape = self.log_shape
        if not all(-1 <= i < log_shape[0] for i in dst_indices):
            raise ValueError(f"dst_indices not in range [-1, {log_shape[0]})")
        if not all(-1 <= i < log_shape[1] for i in src_indices):
            raise ValueError(f"src_indices not in range [-1, {log_shape[1]})")
        if sum(i == -1 for i in src_indices) != sum(i == -1 for i in
        dst_indices):
            raise ValueError("Number of entries equal to -1 between "
            "src_indices and dst_indices is not equal")
        q = self._index.q
        output_shape: tuple[int, int] = (q ** len(dst_indices), q **
        len(src_indices))
        out = ConcreteMatrix.zeros(self._index, output_shape)
        for i, j in product(range(output_shape[0]), range(output_shape[1])):
            ti, idi = self._permutation_index(dst_indices, i, log_shape[0], q)
            tj, idj = self._permutation_index(src_indices, j, log_shape[1], q)
            if idi == idj:
                out[i, j] = self[ti, tj]
        return out

    def _permutation_index(self, indices: list[int], target_index: int, log_dim:
    int, q: int) -> tuple[int, int]:
        """ Given some permutation, get the source index and identity matrix
            index as a tuple, from the target index in the matrix resulting from
            the permutation function. Parameters are the source indices from the
            original matrix, the target index in the new matrix, the log shape
            of the original matrix, and the base Hilbert space dimension q """
        tot, id_index = 0, 0
        powers = []
        for _ in indices:
            powers.append(target_index % q)
            target_index //= q
        powers.reverse()
        for p, index in zip(powers, indices):
            if index == -1:
                id_index *= q
                id_index += p
            else:
                tot += p * q ** (log_dim - index - 1)
        return tot, id_index

    @classmethod
    def _multiply_matrices[Field](cls, left: ConcreteMatrix[Field], right:
    ConcreteMatrix[Field]) -> ConcreteMatrix[Field]:
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
    def _kron_matrices[Field](cls, left: ConcreteMatrix[Field], right:
    ConcreteMatrix[Field]) -> ConcreteMatrix[Field]:
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