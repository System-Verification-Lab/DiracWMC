
from __future__ import annotations
from typing import Iterable, Any, Self
from .abstractmatrix import AbstractMatrix
from .concretematrix import ConcreteMatrix
from ..cnf import CNF, WeightFunction, BoolVar
from ..index import Index, IndexBasisElement

class WCNFMatrix[Field](AbstractMatrix[Field]):
    """ Matrices represented CNF formulae and weight functions on variables """
    
    def __init__(self, index: Index[Field], cnf: CNF, weight_func:
    WeightFunction, input_vars: Iterable[BoolVar], output_vars:
    Iterable[BoolVar]):
        """ Constructor, given the CNF formula, weight function, and input and
            output variables """
        super().__init__(index)
        self._cnf = cnf
        self._weight_func = weight_func
        self._input_vars = list(input_vars)
        self._output_vars = list(output_vars)
        self._log_q = self._calc_log_q(index.q)
        if (len(self._input_vars) % self._log_q != 0 or len(self._output_vars) %
        self._log_q != 0):
            raise ValueError(f"Incorrect input/output var length(s) "
            f"({len(self._input_vars)}, {len(self._output_vars)}) for q = "
            f"{self._index.q} state system")

    def __eq__(self, other: Any) -> bool:
        """ Returns if this matrix is equal to another object. This will only
            return True if the other object is also a WCNFMatrix with the same
            index, such that the two matrices evaluated are equal. This function
            may take a long time since the concrete values of the two matrices
            have to be calculated! """
        if not isinstance(other, WCNFMatrix):
            return False
        if self.index != other.index:
            return False
        return self.value() == other.value()

    @property
    def shape(self) -> tuple[int, int]:
        q = self._index.q
        return (q ** (len(self._output_vars) // self._log_q), q ** (len(
        self._input_vars) // self._log_q))

    @classmethod
    def bra(cls, *elements: IndexBasisElement[Field]) -> Self:
        if len(elements) == 0:
            raise ValueError("Cannot create bra matrix from zero elements")
        q, index = elements[0].index.q, elements[0].index
        log_q = cls._calc_log_q(q)
        cnf = CNF()
        input_vars = []
        for elt in elements:
            elt = elt.value
            cur_vars = [BoolVar() for _ in range(log_q)]
            input_vars += list(reversed(cur_vars))
            for i in range(log_q):
                cnf.add_clause([cur_vars[i] if elt & 1 else -cur_vars[i]])
                elt >>= 1
        weight_func = WeightFunction(input_vars)
        weight_func.fill(1.0)
        return WCNFMatrix(index, cnf, weight_func, input_vars, [])

    @classmethod
    def ket(cls, *elements: IndexBasisElement[Field]) -> Self:
        pass

    @classmethod
    def linear_comb(cls, *elements: tuple[Field, Self] | Self) -> Self:
        pass

    @classmethod
    def product(cls, *elements: Self) -> Self:
        pass

    @classmethod
    def kron(cls, *elements: Self) -> Self:
        pass

    def value(self) -> ConcreteMatrix[Field]:
        return ConcreteMatrix(self._index, [[self._value_at(row, col) for col in
        range(self.shape[1])] for row in range(self.shape[0])])

    def permutation(self, src_indices: Iterable[int], dst_indices: Iterable[int]
    | None = None) -> Self:
        pass

    def copy(self) -> Self:
        pass

    @classmethod
    def _calc_log_q(cls, q: int) -> int:
        """ Returns the log base 2 of q rounded up to the nearest integer """
        amt = 0
        while q > 1:
            if q & 1:
                q += 1
            q >>= 1
            amt += 1
        return amt
    
    @classmethod
    def _to_base(self, val: int, base: int, total: int) -> list[int]:
        """ Determine the representation in the given base of the given value.
            Returns a list in little-endian """
        values = []
        for _ in range(total):
            values.append(val % base)
            val //= base
        if val > 0:
            raise ValueError(f"Given value {val} is too large to represent in "
            f"base {base} with {total} digits")
        values.reverse()
        return values
    
    def _value_at(self, row: int, col: int) -> Field:
        """ Evaluate the value at the given row and column of the matrix """
        cnf = self._cnf.copy()
        q = self._index.q
        row_dim, col_dim = len(self._output_vars) // self._log_q, len(
        self._input_vars) // self._log_q
        row_repr, col_repr = self._to_base(row, q, row_dim), self._to_base(col,
        q, col_dim)
        for i, elt in enumerate(row_repr):
            for j in range(self._log_q):
                var_index = (i + 1) * self._log_q - j - 1
                var = self._output_vars[var_index]
                cnf.add_clause([var if elt & 1 else -var])
                elt >>= 1
        for i, elt in enumerate(col_repr):
            for j in range(self._log_q):
                var_index = (i + 1) * self._log_q - j - 1
                var = self._input_vars[var_index]
                cnf.add_clause([var if elt & 1 else -var])
                elt >>= 1
        return self._weight_func(cnf)

