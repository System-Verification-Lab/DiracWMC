
from itertools import product
from functools import reduce
from typing import Iterable, Iterator, Mapping
from .cnf import CNF, WeightFunction, BoolVar
from ..wcnf import WeightedCNFFormula, CNFFormula, VariableWeights

class WCNFMatrix:
    """ A weighted CNF representation of a 2^n x 2^n matrix, which may be an
        efficient way of representing this matrix in some specific cases """

    PauliX: "WCNFMatrix"
    PauliZ: "WCNFMatrix"

    def __init__(self, cnf: CNF, weight_func: WeightFunction, input_vars: Iterable[BoolVar],
    output_vars: Iterable[BoolVar], condition_var: BoolVar):
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
    
    def __str__(self) -> str:
        """ String representation of the matrix. For small matrices all of the
            entries of the matrix are displayed. Otherwise only the class name
            is returned """
        if self.dimension <= 4:
            out = "["
            length = max(max(len(str(self[i, j])) for j in
            range(self.dimension)) for i in range(self.dimension))
            for i in range(self.dimension):
                if i > 0:
                    out += "\n "
                for j in range(self.dimension):
                    out += str(self[i, j]).rjust(length + 2)
            out += "  ]"
            return out
        out = "["
        length = max(max(len(str(self[i, j])) for j in (0, 1, -1, -2)) for i in
        (0, 1, -1, -2))
        length = max(length, 3)
        for i in (0, 1, 2, -1, -2):
            if i != 0:
                out += "\n "
            if i == 2:
                row = ["...", "...", "", "...", "..."]
            else:
                row = [(str(self[i, j]) if j != 2 else "...") for j in (0, 1, 2,
                -1, -2)]
            for s in row:
                out += s.rjust(length + 2)
        out += " ]"
        return out

    def __getitem__(self, index: tuple[int, int]) -> float:
        """ Get a specific item in the matrix, given its coodinates. Tuple given
            should have the form (row, column). Negative indices are allowed, to
            select a row/column from the end """
        if index[0] < 0:
            index = (index[0] + self.dimension, index[1])
        if index[1] < 0:
            index = (index[0], index[1] + self.dimension)
        cnf = self._cnf.copy()
        for i, v in enumerate(self._output_vars):
            cnf.add_clause([+v if (index[0] >> i) & 1 else -v])
        for i, v in enumerate(self._input_vars):
            cnf.add_clause([+v if (index[1] >> i) & 1 else -v])
        cnf.add_clause([self._condition_var])
        return self._weight_func(cnf)

    def __len__(self) -> int:
        """ The total number of entries in the matrix, which is 2^(2n) """
        return self.size

    def __pow__(self, other: "WCNFMatrix | int") -> "WCNFMatrix":
        """ Compute the kronecker product of this matrix with another, or with
            an integer """
        if isinstance(other, WCNFMatrix):
            return self.__class__.kronecker(self, other)
        return self.__class__.multiply(*((self,) * other))

    def __mul__(self, other: "WCNFMatrix | float") -> "WCNFMatrix":
        """ Compute the matrix product of this matrix with another, or with a
            constant """
        if isinstance(other, WCNFMatrix):
            return self.__class__.multiply(self, other)
        return self.__class__.linear_comb((other, self))

    def __rmul__(self, other: float) -> "WCNFMatrix":
        """ Right multiplication with a constant """
        return self.__class__.linear_comb((other, self))

    def __add__(self, other: "WCNFMatrix") -> "WCNFMatrix":
        """ Compute the sum of this matrix and another """
        return self.__class__.linear_comb(self, other)

    @property
    def size(self) -> int:
        """ The total number of entries in the matrix, which is 2^(2n) """
        return 1 << (2 * self.n)

    @property
    def dimension(self) -> int:
        """ The dimension of the matrix, which is 2^n """
        return 1 << self.n

    @property
    def n(self) -> int:
        """ The logarithmic size of the matrix, such that this matrix is a
            2^n x 2^n matrix """
        return len(self._input_vars)

    @property
    def domain(self) -> Iterable[BoolVar]:
        """ Get an iterable over the domain of variables of the weight function
            of this matrix representation """
        return self._weight_func.domain

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

    def bulk_subst(self, var_map: dict[BoolVar, BoolVar]):
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

    def local_matrix(self, m: int, i: int) -> "WCNFMatrix":
        """ Returns the matrix that is the kronecker product of I_(2^(i)), this
            matrix, and I_(2^(m-i-n)), where n is the number such that 2^n x 2^n
            are the dimensions of this matrix """
        return self.__class__.kronecker(
            self.__class__.identity(i),
            self,
            self.__class__.identity(m - i - self.n)
        )

    @classmethod
    def kronecker(cls, *matrices: "WCNFMatrix") -> "WCNFMatrix":
        """ Compute the kronecker product matrix of one or more other matrices
            """
        assert len(matrices) > 0
        index_map = {}
        index_count = 1
        for i, mat in enumerate(matrices):
            for v in range(1, len(mat._wcnf) + 1):
                if v == mat._condition_var:
                    index_map[i, v] = 1
                    index_map[i, -v] = -1
                else:
                    index_count += 1
                    index_map[i, v] = index_count
                    index_map[i, -v] = -index_count
        wcnf = WeightedCNFFormula(index_count)
        for i, mat in enumerate(matrices):
            wcnf.formula.clauses += [[index_map[i, v] for v in clause] for
            clause in mat._wcnf.formula.clauses]
            for v in range(1, len(mat._wcnf) + 1):
                wcnf.weights[index_map[i, v]] = mat._wcnf.weights[v]
                wcnf.weights[-index_map[i, v]] = mat._wcnf.weights[-v]
        input_vars, output_vars = [], []
        for i, mat in reversed(list(enumerate(matrices))):
            input_vars += [index_map[i, v] for v in mat._input_vars]
            output_vars += [index_map[i, v] for v in mat._output_vars]
        return WCNFMatrix(wcnf, input_vars, output_vars, 1)
    
    @classmethod
    def multiply(cls, *matrices: "WCNFMatrix") -> "WCNFMatrix":
        """ Compute the matrix product of one or more matrices with the same
            dimensions """
        assert len(matrices) > 0
        assert all(mat.n == matrices[0].n for mat in matrices)
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
    def linear_comb(cls, *matrices: "tuple[float, WCNFMatrix] | WCNFMatrix"
    ) -> "WCNFMatrix":
        """ Get the representation of a linear combination of matrices. Each
            matrix can be given as a tuple (factor, matrix) or just the matrix
            itself, meaning factor = 1 """
        matrices = tuple(m if isinstance(m, tuple) else (1.0, m) for m in
        matrices)
        assert len(matrices) > 0
        assert all(m.dimension == matrices[0][1].dimension for _, m in matrices)
        index_map = {}
        index_count = 1
        for i in range(len(matrices) - 1):
            mat, next_mat = matrices[i][1], matrices[i + 1][1]
            for ov, iv in zip(mat._output_vars, next_mat._input_vars):
                if (i, ov) not in index_map:
                    index_count += 1
                    index_map[i, ov] = index_count
                    index_map[i, -ov] = -index_count
                index_map[i + 1, iv] = index_map[i, ov]
                index_map[i + 1, -iv] = index_map[i, -ov]
        for i, (_, mat) in enumerate(matrices):
            for v in range(1, len(mat._wcnf) + 1):
                if (i, v) in index_map:
                    continue
                index_count += 1
                index_map[i, v] = index_count
                index_map[i, -v] = -index_count
        wcnf = WeightedCNFFormula(index_count)
        # Weights
        for v in range(1, index_count + 1):
            wcnf.weights[v] = wcnf.weights[-v] = 1.0
        for i, (_, mat) in enumerate(matrices):
            for v in range(1, len(mat._wcnf) + 1):
                wcnf.weights[index_map[i, v]] *= mat._wcnf.weights[v]
                wcnf.weights[index_map[i, -v]] *= mat._wcnf.weights[-v]
        for i, (factor, mat) in enumerate(matrices):
            wcnf.weights[index_map[i, mat._condition_var]] = factor
        # Clauses
        for i, (_, mat) in enumerate(matrices):
            wcnf.formula.clauses += [[index_map[i, v] for v in clause] for
            clause in mat._wcnf.formula.clauses]
        for i, (_, mati) in enumerate(matrices):
            for j, (_, matj) in enumerate(matrices[i + 1:], i + 1):
                wcnf.formula.clauses.append([-1, index_map[i,
                -mati._condition_var], index_map[j, -matj._condition_var]])
        wcnf.formula.clauses.append([-1, *(index_map[i, mat._condition_var] for
        i, (_,  mat) in enumerate(matrices))])
        for i, (_, mat) in enumerate(matrices):
            wcnf.formula.clauses.append([1, -index_map[i, mat._condition_var]])
        input_vars = [index_map[0, v] for v in matrices[0][1]._input_vars]
        output_vars = [index_map[len(matrices) - 1, v] for v in
        matrices[-1][1]._output_vars]
        return WCNFMatrix(wcnf, input_vars, output_vars, 1)

    @classmethod
    def identity(cls, n: int) -> "WCNFMatrix":
        """ Returns a representation of a 2^n x 2^n identity matrix """
        domain = [BoolVar() for _ in range(n + 1)]
        cnf = CNF([])
        weight_func = WeightFunction(domain)
        weight_func.fill(1.0)
        return WCNFMatrix(cnf, weight_func, domain[:n], domain[:n], domain[-1])
    
    @classmethod
    def zero(cls, n: int) -> "WCNFMatrix":
        """ Returns a representation of a 2^n x 2^n zero matrix """
        domain = [BoolVar() for _ in range(n + 2)]
        c, r = domain[-2], domain[-1]
        cnf = CNF([[-c, r], [c, -r]])
        weight_func = WeightFunction(domain)
        weight_func.fill(1.0)
        weight_func[r, True] = 0.0
        return WCNFMatrix(cnf, weight_func, domain[:n], domain[:n], c)

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

WCNFMatrix.PauliZ = pauli_z()
WCNFMatrix.PauliX = pauli_x()