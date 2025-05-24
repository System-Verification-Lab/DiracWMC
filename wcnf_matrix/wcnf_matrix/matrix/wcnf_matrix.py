
from __future__ import annotations
from functools import reduce
from itertools import product
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

    def __str__(self) -> str:
        """ String representation of the matrix for debugging """
        return (f"{self.__class__.__name__}({self._index}, {self._cnf}, "
        f"{self._weight_func}, {self._input_vars}, {self._output_vars})")

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
        if len(elements) == 0:
            raise ValueError("Cannot determine linear combination of zero "
            "matrices")
        return reduce(lambda x, y: x._add(y), (elt if isinstance(elt,
        WCNFMatrix) else elt[1]._scalar_mult(elt[0]) for elt in elements))

    @classmethod
    def product[Field](cls, *elements: WCNFMatrix[Field]) -> WCNFMatrix[Field]:
        if len(elements) == 0:
            raise ValueError("Cannot determine product of zero matrices")
        return reduce(lambda x, y: x._multiply(y), elements)

    @classmethod
    def kron[Field](cls, *elements: WCNFMatrix[Field]) -> WCNFMatrix[Field]:
        if len(elements) == 0:
            raise ValueError("Cannot determine kronecker product of zero "
            "matrices")
        if not all(elt.index == elements[0].index for elt in elements):
            raise ValueError("Cannot calculate kronecker product of matrices "
            "with different index")
        elements = [elt.copy() for elt in elements]
        return WCNFMatrix(
            elements[0].index,
            reduce(lambda x, y: x & y, (elt._cnf for elt in elements)),
            reduce(lambda x, y: x * y, (elt._weight_func for elt in elements)),
            sum((elt._input_vars for elt in elements), []),
            sum((elt._output_vars for elt in elements), []),
        )

    def value(self) -> ConcreteMatrix[Field]:
        problems = [self._formula_at(i, j) for i, j in product(range(
        self.shape[0]), range(self.shape[1]))]
        results = WeightFunction.batch_model_count(*problems)
        values = [[0.0 for _ in range(self.shape[1])] for _ in range(
        self.shape[0])]
        for (i, j), result in zip(product(range(self.shape[0]), range(
        self.shape[1])), results):
            values[i][j] = result
        return ConcreteMatrix(self._index, values)

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
        new_dims = sum(i == -1 for i in src_indices)
        matrix = self.copy()
        extra_vars = [BoolVar() for _ in range(new_dims * matrix._log_q)]
        matrix._input_vars = matrix._permute_vars(matrix._input_vars,
        extra_vars, src_indices)
        matrix._output_vars = matrix._permute_vars(matrix._output_vars,
        extra_vars, dst_indices)
        extra_weights = WeightFunction(extra_vars)
        extra_weights.fill(1.0)
        matrix._weight_func = matrix._weight_func * extra_weights
        return matrix

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

    def _formula_at(self, row: int, col: int) -> tuple[CNF, WeightFunction]:
        """ Get the CNF formula and weight function that, when evaluated, give a
            model count equal to the entry in this matrix at the given row and
            column """
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
        return (cnf, self._weight_func)

    def _value_at(self, row: int, col: int) -> Field:
        """ Evaluate the value at the given row and column of the matrix """
        cnf, weight_func = self._formula_at(row, col)
        return weight_func(cnf)
    
    def _permute_vars(self, src_vars: list[BoolVar], extra_vars: list[BoolVar],
    src_indices: list[int]) -> list[BoolVar]:
        """ Returns a permutation of the variables from src_vars when they are
            divided into blocks of size log_q. If a source index is -1 a block
            of vars is taken from extra_vars """
        extra_index = 0
        result_vars: list[BoolVar] = []
        for src_index in src_indices:
            if src_index == -1:
                result_vars += extra_vars[extra_index:extra_index + self._log_q]
                extra_index += self._log_q
            else:
                start_index = self._log_q * src_index
                result_vars += src_vars[start_index:start_index + self._log_q]
        return result_vars

    def _scalar_mult(self, factor: float) -> Self:
        """ Returns the matrix that is the result of multiplying the current
            matrix with a scalar factor """
        mat = self.copy()
        if len(mat._weight_func.domain) == 0 or factor == 1.0:
            return mat
        scale_var = next(iter(mat._weight_func.domain))
        mat._weight_func[scale_var, False] *= factor
        mat._weight_func[scale_var, True] *= factor
        return mat

    def _multiply(self, other: Self) -> Self:
        """ Multiply current matrix with another and return the result """
        left, right = self.copy(), other.copy()
        q, index = left.index.q, left.index
        if right.index != index:
            raise ValueError("Cannot calculate product of matrices with "
            "different index")
        log_q = left._log_q
        extra_cnf = CNF()
        if len(left._input_vars) != len(right._output_vars):
            raise ValueError(f"Cannot multiply matrices with shapes "
            f"{left.shape} and {right.shape}")
        left.bulk_subst({i: o for i, o in zip(left._input_vars,
        right._output_vars)})
        for i in range(0, len(right._output_vars), log_q):
            extra_cnf &= self._less_than_cnf(right._output_vars[i:i + log_q], q)
        return WCNFMatrix(
            index,
            extra_cnf & left._cnf & right._cnf,
            left._weight_func * right._weight_func,
            right._input_vars,
            left._output_vars
        )

    def _add(self, other: Self) -> Self:
        """ Add current matrix and another matrix, and return the result """
        left, right = self.copy(), other.copy()
        index = left.index
        if right.index != index:
            raise ValueError("Cannot calculate sum of matrices with different "
            "index")
        if left.shape != right.shape:
            raise ValueError(f"Cannot calculate sum of matrices with different "
            f"shapes {left.shape} and {right.shape}")
        c = BoolVar()
        input_vars = [BoolVar() for _ in left._input_vars]
        output_vars = [BoolVar() for _ in left._output_vars]
        io_weight_func = WeightFunction(input_vars + output_vars)
        io_weight_func.fill(1.0)
        c_weight_func = WeightFunction([c])
        c_weight_func[c, True] = 1.0 / right._weight_func.total_weight()
        c_weight_func[c, False] = 1.0 / left._weight_func.total_weight()
        def link_vars(first: Iterable[BoolVar], second: Iterable[BoolVar]) -> (
        CNF):
            """ Returns the CNF formula x <-> y for all x, y in zip(first,
                second) """
            return CNF(sum(([[x, -y], [-x, y]] for x, y in zip(first, second)),
            []))
        left_cnf = (left._cnf & link_vars(input_vars, left._input_vars) &
        link_vars(output_vars, left._output_vars))
        right_cnf = (right._cnf & link_vars(input_vars, right._input_vars) &
        link_vars(output_vars, right._output_vars))
        return WCNFMatrix(
            index,
            (CNF([[-c]]) | left_cnf) & (CNF([[c]]) | right_cnf),
            left._weight_func * right._weight_func * io_weight_func *
            c_weight_func,
            input_vars,
            output_vars
        )