
from itertools import product
from functools import reduce
from typing import Iterable, Iterator, Mapping, Self
from .cnf import CNF, WeightFunction, BoolVar
from ..wcnf import WeightedCNFFormula, CNFFormula, VariableWeights
from .abstract_matrix import AbstractMatrix

class WCNFMatrix(AbstractMatrix[float]):
    """ A weighted CNF representation of a 2^n x 2^n matrix, which may be an
        efficient way of representing this matrix in some specific cases """

    PauliX: "WCNFMatrix"
    PauliZ: "WCNFMatrix"

    def __init__(self, cnf: CNF, weight_func: WeightFunction, input_vars:
    Iterable[BoolVar], output_vars: Iterable[BoolVar], condition_var: BoolVar):
        """ Constructor, given the CNF formula, weight function, the input and
            output variables, and the conditional variable index """
        self._cnf = cnf
        self._weight_func = weight_func
        self._input_vars = list(input_vars)
        self._output_vars = list(output_vars)
        self._condition_var = condition_var
        self._check_valid()

    def __repr__(self) -> str:
        """ Canonical representation of the matrix """
        return (f"{self.__class__.__name__}({self._cnf!r}, "
        f"{self._weight_func!r}, {self._input_vars!r}, {self._output_vars!r}, "
        f"{self._condition_var!r})")

    @property
    def shape(self) -> tuple[int, int]:
        """ A tuple with the number of rows and columns respectively """
        return 1 << self.n, 1 << self.n

    @property
    def n(self) -> int:
        """ The logarithmic size of the matrix, such that this matrix is a
            2^n x 2^n matrix """
        return len(self._input_vars)

    @property
    def domain(self) -> set[BoolVar]:
        """ Get an iterable over the domain of variables of the weight function
            of this matrix representation """
        return self._weight_func.domain

    def get_entry(self, row: int, col: int) -> float:
        """ Get an entry in the matrix given the row and column """
        cnf = self._cnf.copy()
        for i, v in enumerate(self._output_vars):
            cnf.add_clause([+v if (row >> i) & 1 else -v])
        for i, v in enumerate(self._input_vars):
            cnf.add_clause([+v if (col >> i) & 1 else -v])
        cnf.add_clause([self._condition_var])
        return self._weight_func(cnf)

    def set_entry(self, row: int, col: int, value: float):
        raise NotImplementedError(f"Cannot set entries of matrix class "
        f"{self.__class__.__name__}")

    def scalar_product(self, factor: float) -> Self:
        """ Get the scalar product of this matrix with some factor """
        return self.__class__.linear_comb((factor, self))

    def copy(self) -> "WCNFMatrix":
        """ Make a copy of this WCNF matrix, which uses newly initialized
            variabels """
        matrix = WCNFMatrix(self._cnf.copy(), self._weight_func.copy(), self._input_vars,
        self._output_vars, self._condition_var)
        matrix.replace_vars()
        return matrix

    def replace_vars(self):
        """ Replace all variables in this WCNF matrix object with newly
            initialized ones """
        mapping = {var: BoolVar() for var in self.domain}
        self._cnf.bulk_subst(mapping)
        self._weight_func.bulk_subst(mapping)
        self._input_vars = [mapping[var] for var in self._input_vars]
        self._output_vars = [mapping[var] for var in self._output_vars]
        self._condition_var = mapping[self._condition_var]

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
        self._condition_var = var_map.get(self._condition_var,
        self._condition_var)
        self._cnf.bulk_subst(var_map)
        self._weight_func.bulk_subst(var_map)
        self._check_valid()

    def trace(self) -> "WeightedCNFFormula":
        """ Get a weighted CNF formula such that the total weight of the formula
            is equal to the trace of the matrix """
        cnf = self._cnf.copy()
        cnf.add_clause([self._condition_var])
        for x, y in zip(self._input_vars, self._output_vars):
            if x is not y:
                cnf.add_clause([x, -y], [-x, y])
        return self._weight_func(cnf)

    def exp(self, terms: int) -> "WCNFMatrix":
        """ Get the representation of the matrix sum(k=0..terms-1) matrix^k/k!,
            which is an approximation of e^matrix """
        # TODO: Implement
        assert terms >= 1
        if terms == 1:
            return self.__class__.identity(self.n)
        index_map = {}
        index_count = 1
        for i in range(1, terms - 1):
            for iv, ov in zip(self._input_vars, self._output_vars):
                if (i, ov) not in index_map:
                    index_count += 1
                    index_map[i, ov] = index_count
                    index_map[i, -ov] = -index_count
                index_map[i + 1, iv] = index_map[i, ov]
                index_map[i + 1, -iv] = index_map[i, -ov]
        for i in range(1, terms):
            for v in range(1, len(self._wcnf) + 1):
                if (i, v) in index_map:
                    continue
                index_count += 1
                index_map[i, v] = index_count
                index_map[i, -v] = -index_count
        wcnf = WeightedCNFFormula(index_count)
        # Add clauses
        for i in range(1, terms):
            wcnf.formula.clauses += [[index_map[i, v] for v in clause] for
            clause in self._wcnf.formula.clauses]
        condition_vars = [1, *(index_map[i, self._condition_var] for i in
        range(1, terms))]
        for c1, c2 in zip(condition_vars[:-1], condition_vars[1:]):
            wcnf.formula.clauses.append([-c2, c1])
        # Set weights
        for i in range(1, index_count + 1):
            wcnf.weights[i] = wcnf.weights[-i] = 1.0
        for i, v in product(range(1, terms), range(1, len(self._wcnf) + 1)):
            wcnf.weights[index_map[i, v]] *= self._wcnf.weights[v]
            wcnf.weights[index_map[i, -v]] *= self._wcnf.weights[-v]
        for i, c in enumerate(condition_vars[1:], 1):
            wcnf.weights[c] = 1.0 / i
        input_vars = [index_map[1, v] for v in self._input_vars]
        output_vars = [index_map[terms - 1, v] for v in self._output_vars]
        return WCNFMatrix(wcnf, input_vars, output_vars, 1)

    @classmethod
    def product(cls, *matrices: Self) -> Self:
        """ Get the matrix (dot) product of multiple matrices and return the new
            matrix """
        if len(matrices) <= 0:
            raise ValueError("Cannot determine product of zero matrices")
        if not all(mat.n == matrices[0].n for mat in matrices):
            raise ValueError("Not all matrices in product have the same size")
        matrices = [matrix.copy() for matrix in reversed(matrices)]
        for mat_a, mat_b in zip(matrices, matrices[1:]):
            mat_b.bulk_subst({i: o for i, o in zip(mat_b._input_vars,
            mat_a._output_vars)})
        condition_var = matrices[0]._condition_var
        for mat in matrices:
            mat.subst(mat._condition_var, condition_var)
        return WCNFMatrix(
            reduce(lambda x, y: x & y, (mat._cnf for mat in matrices)),
            reduce(lambda x, y: x * y, (mat._weight_func for mat in matrices)),
            matrices[0]._input_vars,
            matrices[-1]._output_vars,
            condition_var
        )

    @classmethod
    def kronecker(cls, *matrices: Self) -> Self:
        """ Get the kronecker product of multiple matrices and return the new
            matrix """
        if len(matrices) <= 0:
            raise ValueError("Cannot determine kronecker product of zero "
            "matrices")
        matrices = [mat.copy() for mat in reversed(matrices)]
        condition_var = matrices[0]._condition_var
        for mat in matrices:
            mat.subst(mat._condition_var, condition_var)
        return WCNFMatrix(
            reduce(lambda x, y: x & y, (mat._cnf for mat in matrices)),
            reduce(lambda x, y: x * y, (mat._weight_func for mat in matrices)),
            sum((mat._input_vars for mat in matrices), []),
            sum((mat._output_vars for mat in matrices), []),
            condition_var
        )

    @classmethod
    def sum(cls, *matrices: Self) -> Self:
        """ Get the sum of multiple matrices and return the new matrix """
        return cls.linear_comb(*matrices)

    @classmethod
    def identity(cls, size: int) -> Self:
        """ Returns an identity matrix with the given size. The size has to be a
            power of 2 """
        n = log2(size)
        if n == -1:
            raise ValueError(f"Invalid size {size}, must be power of 2")
        domain = [BoolVar() for _ in range(n + 1)]
        cnf = CNF([])
        weight_func = WeightFunction(domain)
        weight_func.fill(1.0)
        return WCNFMatrix(cnf, weight_func, domain[:n], domain[:n], domain[-1])

    @classmethod
    def zero(cls, shape: tuple[int, int]) -> Self:
        """ Returns a zero matrix with the given shape. The shape has to be
            square with lengths powers of 2 """
        if shape[0] != shape[1]:
            raise ValueError(f"Input shape should be square, but is {shape}")
        n = log2(shape[0])
        if n == -1:
            raise ValueError(f"Invalid size {shape[0]}, must be power of 2")
        domain = [BoolVar() for _ in range(n + 2)]
        c, r = domain[-2], domain[-1]
        cnf = CNF([[-c, r], [c, -r]])
        weight_func = WeightFunction(domain)
        weight_func.fill(1.0)
        weight_func[r, True] = 0.0
        return WCNFMatrix(cnf, weight_func, domain[:n], domain[:n], c)

    @classmethod
    def linear_comb(cls, *matrices: "tuple[float, Self] | Self") -> Self:
        """ Get the representation of a linear combination of matrices. Each
            matrix can be given as a tuple (factor, matrix) or just the matrix
            itself, meaning factor = 1 """
        matrices = tuple(mat if isinstance(mat, tuple) else (1.0, mat) for mat
        in matrices)
        matrices = tuple((factor, mat.copy()) for factor, mat in matrices)
        if len(matrices) <= 0:
            raise ValueError("Cannot determine linear combination of zero "
            "matrices")
        if not all(mat.shape == matrices[0][1].shape for _, mat in matrices):
            raise ValueError("Not all matrices in the linear combination have "
            "the same shape")
        for (_, mat_a), (_, mat_b) in zip(matrices, matrices[1:]):
            mat_b.bulk_subst({i: o for i, o in zip(mat_b._input_vars,
            mat_a._output_vars)})
        condition_var = BoolVar()
        cnf = reduce(lambda x, y: x & y, (mat._cnf for _, mat in matrices))
        cnf.add_clause(*([condition_var, -mat._condition_var] for _, mat in
        matrices))
        cnf.add_clause([-condition_var, *(mat._condition_var for _, mat in
        matrices)])
        for i, (_, mat_a) in enumerate(matrices):
            for _, mat_b in matrices[i + 1:]:
                cnf.add_clause([-condition_var, -mat_a._condition_var,
                -mat_b._condition_var])
        weight_func = matrices[0][1]._weight_func
        for _, mat in matrices[1:]:
            weight_func *= mat._weight_func
        weight_func *= WeightFunction([condition_var], weights={condition_var:
        (1.0, 1.0)})
        for factor, mat in matrices:
            weight_func[mat._condition_var, True] = factor
        matrix = WCNFMatrix(cnf, weight_func, matrices[0][1]._input_vars,
        matrices[-1][1]._output_vars, condition_var)
        return matrix

    def _check_valid(self):
        """ Check if the matrix representation is valid. If it is not, raise the
            appropriate exception """
        # TODO
        return True
        for i, v in enumerate(self._input_vars):
            if not 0 < v <= len(self._wcnf):
                raise ValueError(f"Invalid variable in input variables: {v}, "
                f"valid range [1, {len(self._wcnf)}]")
            for j, w in enumerate(self._input_vars):
                if i != j and v == w:
                    raise ValueError(f"Duplicate variable {v} in input "
                    f"variables")
            for j, w in enumerate(self._output_vars):
                if i != j and v == w:
                    raise ValueError(f"Invalid duplicate variable between "
                    f"input and output variables: {v}")
        for i, v in enumerate(self._output_vars):
            if not 0 < v <= len(self._wcnf):
                raise ValueError(f"Invalid variable in output variables: {v}, "
                f"valid range [1, {len(self._wcnf)}]")
            for j, w in enumerate(self._output_vars):
                if i != j and v == w:
                    raise ValueError(f"Duplicate variable {v} in output "
                    "variables")
        if (self._condition_var in self._input_vars or self._condition_var in
        self._output_vars):
            raise ValueError("Condition variable may not appear in input and "
            "output variabels")
        if not 0 < self._condition_var <= len(self._wcnf):
            raise ValueError(f"Invalid conditional variable "
            f"{self._condition_var}")
        if (self._wcnf.weights[self._condition_var] != 1.0 or
        self._wcnf.weights[self._condition_var] != 1.0):
            raise ValueError("Weight of conditional variable should be 1.0")
        if len(self._input_vars) != len(self._output_vars):
            raise ValueError(f"Input variable length not equal to output "
            f"variable length: {len(self._input_vars)} != "
            f"{len(self._output_vars)}")

def pauli_z() -> WCNFMatrix:
    """ Constructs a Pauli Z matrix with newly initialized variables """
    r, x, c = BoolVar(), BoolVar(), BoolVar()
    # r <-> (x and c)
    cnf = CNF([[-r, x], [-r, c], [r, -x, -c]])
    weight_func = WeightFunction([r, x, c])
    weight_func.fill(1.0)
    weight_func[r, True] = -1.0
    return WCNFMatrix(cnf, weight_func, [x], [x], c)

def pauli_x() -> WCNFMatrix:
    """ Constructs a Pauli X matrix with newly initialized variables """
    x, y, c = BoolVar(), BoolVar(), BoolVar()
    # y <-> (x XOR c)
    cnf = CNF([[-y, x, c], [-y, -x, -c], [y, x, -c], [y, -x, c]])
    weight_func = WeightFunction([x, y, c])
    weight_func.fill(1.0)
    return WCNFMatrix(cnf, weight_func, [x], [y], c)

def log2(x: int) -> int:
    """ Get the log2 of a number, or -1 if x is not a perfect power of 2 """
    last_one = False
    if x < 1:
        return -1
    lg = 0
    while x > 1:
        if last_one:
            return -1
        if x & 1:
            last_one = True
        x >>= 1
        lg += 1
    return lg

WCNFMatrix.PauliZ = pauli_z()
WCNFMatrix.PauliX = pauli_x()