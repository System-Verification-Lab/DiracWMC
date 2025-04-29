
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
        """ The shape of the matrix as a tuple (rows, columns) """
        return (len(self._values), len(self._values[0]))
    
    @property
    def log_shape(self) -> tuple[int, int]:
        """ The shape of the matrix log base q. If these values are not both
            integers, a RuntimeError is thrown """
        q = self._index.q
        def exact_log(val: int) -> int:
            out = 0
            while val > 1:
                if val % q != 0:
                    raise RuntimeError("Log of matrix shape is not exact")
                val //= q
                out += 1
            return out
        return exact_log(self.shape[0]), exact_log(self.shape[1])

    def copy(self) -> ConcreteMatrix[Field]:
        return ConcreteMatrix(self._index, self._values)

    def value(self) -> ConcreteMatrix[Field]:
        return self.copy()

    def permutation(self, src_indices: Iterable[int]) -> Self:
        src_indices = list(src_indices)
        log_shape = self.log_shape
        if log_shape[0] != log_shape[1]:
            raise RuntimeError("Permutation can only be applied on square"
            "matrices")
        log_dim = self.log_shape[0]
        if not all(-1 <= i < log_dim for i in src_indices):
            raise ValueError(f"src_indices not in range [-1, {log_dim})")
        q = self._index.q
        output_dim: int = q ** len(src_indices)
        q_powers, qpow = [], 1
        for _ in range(log_dim):
            q_powers.append(qpow)
            qpow *= q
        q_powers.reverse()
        def get_index(index: int) -> tuple[int, int]:
            """ Returns a tuple (source index, identity index) """
            tot, id_index = 0, 0
            powers = []
            for _ in src_indices:
                powers.append(index % q)
                index //= q
            powers.reverse()
            for i, target_index in enumerate(src_indices):
                cur_index = powers[i]
                if target_index == -1:
                    id_index *= q
                    id_index += cur_index
                else:
                    tot += q_powers[target_index] * cur_index
            return tot, id_index
        out = ConcreteMatrix.zeros(self._index, (output_dim, output_dim))
        for i, j in product(range(output_dim), range(output_dim)):
            (di, die), (dj, dje) = get_index(i), get_index(j)
            if die == dje:
                out[i, j] = self[di, dj]
        return out

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