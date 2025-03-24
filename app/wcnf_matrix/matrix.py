
from itertools import product
from typing import Iterable
from ..wcnf import WeightedCNFFormula, CNFFormula, VariableWeights

class WCNFMatrix:
    """ A weighted CNF representation of a 2^n x 2^n matrix, which may be an
        efficient way of representing this matrix in some specific cases """

    PauliX: "WCNFMatrix"
    PauliZ: "WCNFMatrix"

    def __init__(self, wcnf: WeightedCNFFormula, input_vars: Iterable[int],
    output_vars: Iterable[int], condition_var: int):
        """ Constructor, given the weighed CNF formula, the input and output
            variables, and the conditional variable index """
        input_vars = list(input_vars)
        output_vars = list(output_vars)
        self._wcnf = wcnf
        self._input_vars = input_vars
        self._output_vars = output_vars
        self._condition_var = condition_var
        assert all(0 < v <= len(wcnf) for v in input_vars)
        assert all(0 < v <= len(wcnf) for v in output_vars)
        assert (condition_var not in input_vars and condition_var not in
        output_vars)
        assert 0 < condition_var <= len(wcnf)
        assert (wcnf.weights[condition_var] == wcnf.weights[-condition_var] ==
        1.0)
        assert len(input_vars) == len(output_vars)

    def __repr__(self) -> str:
        """ Canonical representation of the matrix """
        return (f"{self.__class__.__name__}({self._wcnf!r}, "
        f"{self._input_vars!r}, {self._output_vars!r}, "
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
        wcnf = self._wcnf.copy()
        wcnf.formula.clauses.append([self._condition_var])
        for i, v in enumerate(self._output_vars):
            wcnf.formula.clauses.append([v if (index[0] >> i) & 1 else -v])
        for i, v in enumerate(self._input_vars):
            wcnf.formula.clauses.append([v if (index[1] >> i) & 1 else -v])
        return wcnf.total_weight()

    def __len__(self) -> int:
        """ The total number of entries in the matrix, which is 2^(2n) """
        return self.size

    def __pow__(self, other: "WCNFMatrix") -> "WCNFMatrix":
        """ Compute the kronecker product of this matrix with another """
        return self.__class__.kronecker(self, other)

    def __mul__(self, other: "WCNFMatrix") -> "WCNFMatrix":
        """ Compute the matrix product of this matrix with another """
        return self.__class__.multiply(self, other)

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

    def trace(self) -> "WeightedCNFFormula":
        """ Get a weighted CNF formula such that the total weight of the formula
            is equal to the trace of the matrix """
        wcnf = self._wcnf.copy()
        wcnf.formula.clauses.append([self._condition_var])
        for x, y in zip(self._input_vars, self._output_vars):
            wcnf.formula.clauses += [[x, -y], [-x, y]]
        return wcnf

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
        assert all(m.dimension == matrices[0].dimension for m in matrices)
        matrices = tuple(reversed(matrices))
        index_map = {}
        index_count = 1
        for i, mat in enumerate(matrices):
            index_map[i, mat._condition_var] = 1
            index_map[i, -mat._condition_var] = -1
        for i in range(len(matrices) - 1):
            mat = matrices[i]
            next_mat = matrices[i + 1]
            for ov, iv in zip(mat._output_vars, next_mat._input_vars):
                if (i, ov) not in index_map:
                    index_count += 1
                    index_map[i, ov] = index_count
                    index_map[i, -ov] = -index_count
                index_map[i + 1, iv] = index_map[i, ov]
                index_map[i + 1, -iv] = index_map[i, -ov]
        for i, mat in enumerate(matrices):
            for v in range(1, len(mat._wcnf) + 1):
                if (i, v) in index_map:
                    continue
                index_count += 1
                index_map[i, v] = index_count
                index_map[i, -v] = -index_count
        wcnf = WeightedCNFFormula(index_count)
        # Set correct weights
        for v in range(1, index_count + 1):
            wcnf.weights[v] = wcnf.weights[-v] = 1.0
        for i, mat in enumerate(matrices):
            for v in range(1, len(mat._wcnf) + 1):
                wcnf.weights[index_map[i, v]] *= mat._wcnf.weights[v]
                wcnf.weights[-index_map[i, v]] *= mat._wcnf.weights[-v]
        # Add clauses
        for i, mat in enumerate(matrices):
            wcnf.formula.clauses += [[index_map[i, v] for v in clause] for
            clause in mat._wcnf.formula.clauses]
        input_vars = [index_map[0, v] for v in matrices[0]._input_vars]
        output_vars = [index_map[len(matrices) - 1, v] for v in
        matrices[-1]._output_vars]
        return WCNFMatrix(wcnf, input_vars, output_vars, 1)

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
        print(wcnf)
        return WCNFMatrix(wcnf, input_vars, output_vars, 1)

    @classmethod
    def identity(cls, n: int) -> "WCNFMatrix":
        """ Returns a representation of a 2^n x 2^n identity matrix """
        return WCNFMatrix(WeightedCNFFormula(n + 1,
            formula=CNFFormula(n + 1, clauses=[]),
            weights=VariableWeights(n + 1, weights={
                **{v: 1.0 for v in range(1, n + 2)},
                **{-v: 1.0 for v in range(1, n + 2)},
            })
        ), list(range(1, n + 1)), list(range(1, n + 1)), n + 1)
    
    @classmethod
    def zero(cls, n: int) -> "WCNFMatrix":
        """ Returns a representation of a 2^n x 2^n zero matrix """
        return WCNFMatrix(WeightedCNFFormula(n + 2,
            formula=CNFFormula(n + 2, clauses=[[-(n + 1), n + 2], [n + 1,
            -(n + 2)]]),
            weights=VariableWeights(n + 2, weights={
                n + 2: 0.0,
                -(n + 2): 1.0,
                **{v: 1.0 for v in range(1, n + 2)},
                **{-v: 1.0 for v in range(1, n + 2)},
            })
        ), list(range(1, n + 1)), list(range(1, n + 1)), n + 1)

WCNFMatrix.PauliZ = WCNFMatrix(WeightedCNFFormula(3,
    formula=CNFFormula(3, clauses=[[-1, 2], [-1, 3], [1, -2, -3]]),
    weights=VariableWeights(3, weights={
        1: -1.0, -1: 1.0,
        **{v: 1.0 for v in (2, 3)},
        **{-v: 1.0 for v in (2, 3)},
    })
), [2], [2], 3)
WCNFMatrix.PauliX = WCNFMatrix(WeightedCNFFormula(3,
    formula=CNFFormula(3, clauses=[[1, -2, 3], [-1, -2, -3], [-1, 2, 3], [1, 2,
    -3]]),
    weights=VariableWeights(3, weights={
        **{v: 1.0 for v in (1, 2, 3)},
        **{-v: 1.0 for v in (1, 2, 3)},
    })
), [1], [2], 3)