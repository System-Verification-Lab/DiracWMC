
from __future__ import annotations
from functools import reduce
from typing import Iterable, Any, Self, Mapping
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
    def bra[Field](cls, *elements: IndexBasisElement[Field]) -> WCNFMatrix[
    Field]:
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
    def ket[Field](cls, *elements: IndexBasisElement[Field]) -> WCNFMatrix[
    Field]:
        if len(elements) == 0:
            raise ValueError("Cannot create ket matrix from zero elements")
        q, index = elements[0].index.q, elements[0].index
        log_q = cls._calc_log_q(q)
        cnf = CNF()
        output_vars = []
        for elt in elements:
            elt = elt.value
            cur_vars = [BoolVar() for _ in range(log_q)]
            output_vars += list(reversed(cur_vars))
            for i in range(log_q):
                cnf.add_clause([cur_vars[i] if elt & 1 else -cur_vars[i]])
                elt >>= 1
        weight_func = WeightFunction(output_vars)
        weight_func.fill(1.0)
        return WCNFMatrix(index, cnf, weight_func, [], output_vars)

    @classmethod
    def linear_comb[Field](cls, *elements: tuple[Field, WCNFMatrix[Field]] |
    WCNFMatrix[Field]) -> WCNFMatrix[Field]:
        ...

    @classmethod
    def product[Field](cls, *elements: WCNFMatrix[Field]) -> WCNFMatrix[Field]:
        if len(elements) == 0:
            raise ValueError("Cannot determine product of zero matrices")
        q, index = elements[0].index.q, elements[0].index
        if not all(elt.index == elements[0].index for elt in elements):
            raise ValueError("Cannot calculate product of matrices with "
            "different index")
        log_q = elements[0]._log_q
        elements = [elt.copy() for elt in reversed(elements)]
        extra_cnf = CNF()
        for elt_a, elt_b in zip(elements, elements[1:]):
            if len(elt_a._output_vars) != len(elt_b._input_vars):
                raise ValueError(f"Cannot multiply matrices with shapes "
                f"{elt_b.shape} and {elt_a.shape}")
            elt_b.bulk_subst({i: o for i, o in zip(elt_b._input_vars,
            elt_a._output_vars)})
            for i in range(0, len(elt_a._output_vars), log_q):
                extra_cnf &= cls._less_than_cnf(elt_a._output_vars[i:i + log_q],
                q)
        return WCNFMatrix(
            index,
            extra_cnf & reduce(lambda x, y: x & y, (elt._cnf for elt in
            elements)),
            reduce(lambda x, y: x * y, (elt._weight_func for elt in elements)),
            elements[0]._input_vars,
            elements[-1]._output_vars
        )

    @classmethod
    def kron[Field](cls, *elements: WCNFMatrix[Field]) -> WCNFMatrix[Field]:
        ...

    def value(self) -> ConcreteMatrix[Field]:
        return ConcreteMatrix(self._index, [[self._value_at(row, col) for col in
        range(self.shape[1])] for row in range(self.shape[0])])

    def permutation(self, src_indices: Iterable[int], dst_indices: Iterable[int]
    | None = None) -> Self:
        ...

    def copy(self) -> Self:
        matrix = WCNFMatrix(self.index, self._cnf.copy(),
        self._weight_func.copy(), self._input_vars, self._output_vars)
        matrix.replace_vars()
        return matrix

    def replace_vars(self):
        """ Replace all variables in this WCNFMatrix object with newly
            initialized ones """
        mapping = {var: BoolVar() for var in self.domain}
        self._cnf.bulk_subst(mapping)
        self._weight_func.bulk_subst(mapping)
        self._input_vars = [mapping[var] for var in self._input_vars]
        self._output_vars = [mapping[var] for var in self._output_vars]

    def subst(self, find: BoolVar, replace: BoolVar):
        """ Substitute the given variable in the representation with another """
        if find == replace:
            return
        self.bulk_subst({find: replace})

    def bulk_subst(self, var_map: Mapping[BoolVar, BoolVar]):
        """ Bulk substitute variables. This also allows for substitutions like
            {x: y, y: x} """
        self._input_vars = [var_map.get(var, var) for var in self._input_vars]
        self._output_vars = [var_map.get(var, var) for var in self._output_vars]
        self._cnf.bulk_subst(var_map)
        self._weight_func.bulk_subst(var_map)

    @property
    def domain(self) -> set[BoolVar]:
        """ Get an iterable over the domain of variables of the weight function
            of this matrix representation """
        return self._weight_func.domain

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
    def _to_base(cls, val: int, base: int, total: int) -> list[int]:
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
    
    @classmethod
    def _less_than_cnf(cls, bool_vars: Iterable[BoolVar], q: int) -> CNF:
        """ Returns a CNF formula that represents that the little endian binary
            representation of the given bool variables is (strictly) less than q
            """
        bool_vars = list(bool_vars)
        bin_q = bin(q - 1)[2:]
        if len(bin_q) > len(bool_vars):
            return CNF()
        bin_q.zfill(len(bool_vars))
        cnf = CNF()
        pos_vars: list[BoolVar] = []
        for var, digit in zip(bool_vars, bin_q):
            if digit == "1":
                pos_vars.append(var)
            else:
                cnf.add_clause([-var, *(-v for v in pos_vars)])
        return cnf

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
