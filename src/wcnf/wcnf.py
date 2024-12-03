
from typing import Iterable
from itertools import product

class WeightedCNF:
    """ Represents a weighted CNF formula. Variables are 1-indexed in clauses
        and weights lists """

    def __init__(self, num_vars: int):
        """ Constructor, given the number of variables """
        self._num_vars = num_vars
        # First half corresponds to negations
        self._weights: list[float | None] = [None] * (num_vars * 2 + 1)
        # Negative variables correspond to negations
        self.clauses: list[list[int]] = []

    @classmethod
    def from_string(cls, text: str) -> "WeightedCNF":
        """ Constructed weighted CNF formula from a standard CNF format """
        formula: WeightedCNF | None = None
        sum_vars: set[int] = set()
        for line in map(str.strip, text.split("\n")):
            if line.startswith("c") or len(line) == 0:
                continue
            if line.startswith(("p cnf", "p show")):
                _, cmd, *args = line.split()
                if cmd == "cnf":
                    assert formula is None
                    formula = cls(int(args[0]))
                else:
                    sum_vars = set(filter(lambda i: i != 0, map(int, args)))
            else:
                assert formula is not None
                formula._parse_cnf_line(line)
        assert formula is not None
        for var in sum_vars:
            if (formula.get_weight(var) is None and formula.get_weight(-var) is
            None):
                formula.set_weight(var, 1.0)
                formula.set_weight(-var, 1.0)
            elif formula.get_weight(var) is None:
                formula.set_weight(var, 1.0 - formula.get_weight(-var))
            elif formula.get_weight(-var) is None:
                formula.set_weight(-var, 1.0 - formula.get_weight(var))
        return formula

    def to_string(self) -> str:
        """ Convert this weighted CNF object to a standard CNF format text """
        text: list[str] = []
        # CNF description
        text.append(f"p cnf {self._num_vars} {len(self.clauses)}")
        # Sum-vars
        sum_vars = [i for i in range(1, self._num_vars + 1) if
        self.get_weight(i) is not None or self.get_weight(-i) is not None]
        vars_string = "".join(map(lambda i: str(i) + " ", sum_vars))
        text.append(f"p show {vars_string}0")
        # Variable weights
        for i in range(-self._num_vars, self._num_vars + 1):
            if i == 0:
                continue
            if self.get_weight(i) is not None:
                text.append(f"p weight {i} {self.get_weight(i)}")
        # Clauses
        for clause in self.clauses:
            vars_string = "".join(map(lambda i: str(i) + " ", clause))
            text.append(f"{vars_string}0")
        return "\n".join(text)

    def set_weight(self, var: int, weight: float | None):
        """ Set the weight of a variable. If variable is negative, set the
            weight of the negation """
        assert var != 0
        self._weights[var + self._num_vars] = weight

    def get_weight(self, var: int) -> float | None:
        """ Get the weight of a variable given its truth value (sign) """
        assert var != 0
        return self._weights[var + self._num_vars]

    def total_weight(self) -> float:
        """ Get the summer weight over all assignments of truth values of all
            variables. This is a brute force method, and therefore slow """
        total = 0.0
        for assignment in product([False, True], repeat=self._num_vars):
            total += self.assignment_weight(assignment)
        return total

    def assignment_weight(self, assignment: Iterable[bool], ignore_truth: bool =
    False) -> float:
        """ Get the weight given a specific assignment of variables. If
            ignore_truth is set to True this function will not return 0 when the
            truth value of the formula is False """
        if not ignore_truth and self.assignment_truth(assignment):
            return 0.0
        total = 1.0
        for i, value in enumerate(assignment, 1):
            i = i if value else -i
            weight = self.get_weight(i)
            if weight is not None:
                total += weight
        return total

    def assignment_truth(self, assignment: Iterable[bool]) -> bool:
        """ Check if the given assignment of variables makes the formula true
            """
        assignment = list(assignment)
        return all(self._clause_truth(clause, assignment) for clause in
        self.clauses)

    def __len__(self) -> int:
        """ Get the number of variables in the formula """
        return self._num_vars
    
    def __str__(self) -> str:
        """ Convert this weighted CNF object to a standard CNF format text """
        return self.to_string()
    
    def _parse_cnf_line(self, line: str):
        """ Parse a line in a CNF-formatted string and apply the given
            instruction to this object """
        if line.startswith("p weight"):
            # Add weight to variable
            var, weight = line.split()[2:]
            self.set_weight(int(var), float(weight))
        else:
            # Add clause
            self.clauses.append(list(filter(lambda i: i != 0, map(int,
            line.split()))))

    def _clause_truth(self, clause: list[int], assignment: list[bool]) -> bool:
        """ Check if the given clause holds, given assignment of variables """
        for i in clause:
            target = i > 0
            if assignment[abs(i) - 1] == target:
                return True
        return False