
from __future__ import annotations
from functools import reduce
from itertools import product, chain
from typing import Iterable, Any, Self, Mapping
from .abstractmatrix import AbstractMatrix
from .concretematrix import ConcreteMatrix
from ..cnf import CNF, WeightFunction, BoolVar
from ..index import Index, IndexBasisElement
from .varrep import VarRep, LogVarRep

var_rep_type: type[VarRep] = LogVarRep

def set_var_rep_type(var_rep: type[VarRep]):
    """ Set the default type of number encoding used in WCNFMatrix objects. Note
        that performing operations on two matrices with different encodings in
        unsupported. This function should therefore be called before any
        WCNFMatrix objects are created. Initially this is set to LogVarRep """
    global var_rep_type
    var_rep_type = var_rep

def get_var_rep_type() -> type[VarRep]:
    """ Get the default type of number encoding used in WCNFMatrix objects """
    return var_rep_type

class WCNFMatrix[Field](AbstractMatrix[Field]):
    """ Matrices represented CNF formulae and weight functions on variables """
    
    def __init__(self, index: Index[Field], cnf: CNF, weight_func:
    WeightFunction, input_vars: Iterable[VarRep], output_vars:
    Iterable[VarRep]):
        """ Constructor, given the CNF formula, weight function, and input and
            output variable representations. These variable representations have
            to be of the type currently set as default, and have to have base q
            """
        super().__init__(index)
        self._cnf = cnf
        self._weight_func = weight_func
        self._input_vars = list(i.copy() for i in input_vars)
        self._output_vars = list(o.copy() for o in output_vars)
        if (not all(isinstance(i, var_rep_type) and i.q == index.q for i in
        self._input_vars) or not all(isinstance(o, var_rep_type) and o.q ==
        index.q for o in self._output_vars)):
            raise ValueError("Invalid input/output vars passed to WCNFMatrix")

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
        return (q ** len(self._output_vars), q ** len(self._input_vars))

    @classmethod
    def bra[Field](cls, *elements: IndexBasisElement[Field]) -> WCNFMatrix[
    Field]:
        if len(elements) == 0:
            raise ValueError("Cannot create bra matrix from zero elements")
        q, index = elements[0].index.q, elements[0].index
        cnf = CNF()
        input_vars = []
        var_reps = []
        for elt in elements:
            elt = elt.value
            if not 0 <= elt < q:
                raise ValueError(f"Value of bra has to be in range 0,...,q-1, "
                f"got {elt}")
            var_rep = var_rep_type(q)
            cnf &= var_rep.equals(elt)
            input_vars += list(var_rep.domain())
            var_reps.append(var_rep)
        weight_func = WeightFunction(input_vars)
        weight_func.fill(1.0)
        return WCNFMatrix(index, cnf, weight_func, var_reps, [])

    @classmethod
    def ket[Field](cls, *elements: IndexBasisElement[Field]) -> WCNFMatrix[
    Field]:
        if len(elements) == 0:
            raise ValueError("Cannot create ket matrix from zero elements")
        q, index = elements[0].index.q, elements[0].index
        cnf = CNF()
        output_vars = []
        var_reps = []
        for elt in elements:
            elt = elt.value
            if not 0 <= elt < q:
                raise ValueError(f"Value of ket has to be in range 0,...,q-1, "
                f"got {elt}")
            var_rep = var_rep_type(q)
            cnf &= var_rep.equals(elt)
            output_vars += list(var_rep.domain())
            var_reps.append(var_rep)
        weight_func = WeightFunction(output_vars)
        weight_func.fill(1.0)
        return WCNFMatrix(index, cnf, weight_func, [], var_reps)

    @classmethod
    def identity[Field](cls, index: Index[Field], size: int) -> WCNFMatrix[
    Field]:
        io_vars = [var_rep_type(index.q) for _ in range(size)]
        weight_func = WeightFunction(chain(*(v.domain() for v in io_vars)))
        weight_func.fill(1.0)
        return WCNFMatrix(index, CNF(), weight_func, io_vars, io_vars)

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
        extra_vars = [var_rep_type(matrix.index.q) for _ in range(new_dims)]
        matrix._input_vars = matrix._permute_vars(matrix._input_vars,
        extra_vars, src_indices)
        matrix._output_vars = matrix._permute_vars(matrix._output_vars,
        extra_vars, dst_indices)
        extra_weights = WeightFunction(extra_vars)
        extra_weights.fill(1.0)
        matrix._weight_func *= extra_weights
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
        for var in chain(self._input_vars, self._output_vars):
            var.substitute(mapping)

    def subst(self, find: BoolVar, replace: BoolVar):
        """ Substitute the given variable in the representation with another """
        if find == replace:
            return
        self.bulk_subst({find: replace})

    def bulk_subst(self, var_map: Mapping[BoolVar, BoolVar]):
        """ Bulk substitute variables. This also allows for substitutions like
            {x: y, y: x} """
        var_map = dict(var_map)
        for var in chain(self._input_vars, self._output_vars):
            var.substitute(var_map)
        self._cnf.bulk_subst(var_map)
        self._weight_func.bulk_subst(var_map)

    def trace_formula(self) -> tuple[CNF, WeightFunction]:
        """ Get the CNF formula and weight function such that the model count of
            the formula w.r.t. the weight function is equal to the trace of this
            matrix """
        matrix_copy = self.copy()
        for iv, ov in zip(matrix_copy._input_vars, matrix_copy._output_vars):
            matrix_copy._cnf &= iv.equals_other(ov)
        return matrix_copy._cnf, matrix_copy._weight_func

    @property
    def domain(self) -> set[BoolVar]:
        """ Get an iterable over the domain of variables of the weight function
            of this matrix representation """
        return self._weight_func.domain
    
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

    def _formula_at(self, row: int, col: int) -> tuple[CNF, WeightFunction]:
        """ Get the CNF formula and weight function that, when evaluated, give a
            model count equal to the entry in this matrix at the given row and
            column """
        cnf = self._cnf.copy()
        q = self._index.q
        row_dim, col_dim = len(self._output_vars), len(self._input_vars)
        row_repr, col_repr = self._to_base(row, q, row_dim), self._to_base(col,
        q, col_dim)
        for var, num in zip(reversed(self._output_vars), row_repr):
            cnf &= var.equals(num)
        for var, num in zip(reversed(self._input_vars), col_repr):
            cnf &= var.equals(num)
        return cnf, self._weight_func.copy()
    
    def _permute_vars(self, src_vars: list[VarRep], extra_vars: list[VarRep],
    src_indices: list[int]) -> list[VarRep]:
        """ Returns a permutation of the variables from src_vars. If a source
            index is -1 a VarRep is taken from extra_vars """
        extra_index = 0
        result_vars: list[VarRep] = []
        for src_index in src_indices:
            if src_index == -1:
                result_vars.append(extra_vars[extra_index])
                extra_index += 1
            else:
                result_vars.append(src_vars[src_index])
        return result_vars

    def _scalar_mult(self, factor: float) -> Self:
        """ Returns the matrix that is the result of multiplying the current
            matrix with a scalar factor """
        mat = self.copy()
        extra_var = BoolVar()
        mat._weight_func = mat._weight_func * WeightFunction([extra_var],
        weights={extra_var: (factor, factor)})
        mat._cnf.add_clause([extra_var])
        return mat

    def _multiply(self, other: Self) -> Self:
        """ Multiply current matrix with another and return the result """
        left, right = self.copy(), other.copy()
        index = left.index
        if right.index != index:
            raise ValueError("Cannot calculate product of matrices with "
            "different index")
        extra_cnf = CNF()
        if len(left._input_vars) != len(right._output_vars):
            raise ValueError(f"Cannot multiply matrices with shapes "
            f"{left.shape} and {right.shape}")
        subst_map = {}
        for iv, ov in zip(left._input_vars, right._output_vars):
            for i, o in zip(iv.domain(), ov.domain()):
                subst_map[i] = o
        left.bulk_subst(subst_map)
        for var in right._output_vars:
            extra_cnf &= var.less_than_q()
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
        q, index = left.index.q, left.index
        if right.index != index:
            raise ValueError("Cannot calculate sum of matrices with different "
            "index")
        if left.shape != right.shape:
            raise ValueError(f"Cannot calculate sum of matrices with different "
            f"shapes {left.shape} and {right.shape}")
        c = BoolVar()
        input_vars = [var_rep_type(q) for _ in left._input_vars]
        output_vars = [var_rep_type(q) for _ in left._output_vars]
        io_weight_func = WeightFunction(sum((list(var.domain()) for var in
        chain(input_vars, output_vars)), []))
        io_weight_func.fill(1.0)
        c_weight_func = WeightFunction([c])
        c_weight_func[c, True] = 1.0 / right._weight_func.total_weight()
        c_weight_func[c, False] = 1.0 / left._weight_func.total_weight()
        def link_vars(first: Iterable[VarRep], second: Iterable[VarRep]) -> (
        CNF):
            """ Returns the CNF formula x <-> y for all x, y in zip(first,
                second) """
            cnf = CNF()
            for x, y in zip(first, second):
                cnf &= x.equals_other(y)
            return cnf
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