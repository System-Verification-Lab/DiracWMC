
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
            return ("[\n" + "\n".join("    [" + ", ".join(str(self[i, j]) for j
            in range(self.dimension)) + "]," for i in range(self.dimension)) +
            "\n]")
        return f"<{self.__class__.__name__}>"

    def __getitem__(self, index: tuple[int, int]) -> float:
        """ Get a specific item in the matrix, given its coodinates. Tuple given
            should have the form (row, column) """
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

    @classmethod
    def kronecker(self, *matrices: "WCNFMatrix") -> "WCNFMatrix":
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
    def multiply(self, *matrices: "WCNFMatrix") -> "WCNFMatrix":
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
                index_count += 1
                index_map[i + 1, iv] = index_map[i, ov] = index_count
                index_map[i + 1, -iv] = index_map[i, -ov] = -index_count
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

    @property
    def size(self) -> int:
        """ The total number of entries in the matrix, which is 2^(2n) """
        return 1 << (2 * len(self._input_vars))

    @property
    def dimension(self) -> int:
        """ The dimension of the matrix, which is 2^n """
        return 1 << len(self._input_vars)
    
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