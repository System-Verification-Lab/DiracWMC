
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

    def set_weight(self, var: int, weight: float | None):
        """ Set the weight of a variable. If variable is negative, set the
            weight of the negation """
        assert var != 0
        self._weights[var + self._num_vars] = weight

    def get_weight(self, var: int) -> float | None:
        """ Get the weight of a variable given its truth value (sign) """
        assert var != 0
        return self._weights[var + self._num_vars]

    def add_missing_weights(self):
        """ Add any weights that are not set. If a x is set but -x is not (or
            vice versa), then weight(-x) = 1 - weight(x). If neither x nor -x is
            set, then weight(-x) = weight(x) = 0.5 """
        for i in self.vars():
            has_pos = self.get_weight(i) is not None
            has_neg = self.get_weight(-i) is not None
            if not has_pos and not has_neg:
                self.set_weight(i, 0.5)
                self.set_weight(i, 0.5)
            elif not has_pos:
                self.set_weight(i, 1 - self.get_weight(-i))
            elif not has_neg:
                self.set_weight(-i, 1 - self.get_weight(i))

    def normalize_weights(self) -> float:
        """ Normalize the weights of this CNF formula to have weight(-x) +
            weight(x) = 1. This raises an exception if not all weights are set
            or one of the weights is negative (both positive and negative
            variables need to be set). Returns the normalization factor that the
            resulting total weight would have to be multiplied with """
        factor = 1.0
        for i in range(1, self._num_vars + 1):
            pos, neg = self.get_weight(i), self.get_weight(-i)
            assert pos is not None and neg is not None
            assert pos >= 0.0 and neg >= 0.0
            total = pos + neg
            assert total > 0.0
            factor *= total
            if total == 0.0:
                self.set_weight(i, 0.5)
                self.set_weight(-i, 0.5)
            else:
                self.set_weight(i, pos / total)
                self.set_weight(-i, neg / total)
        return factor

    def total_weight(self, ignore_truth: bool = False) -> float:
        """ Get the summed weight over all assignments of truth values of all
            variables. This is a brute force method, and therefore slow. If
            ignore_truth is set to True this function will return the sum of all
            weights, irrespective of whether the configurations satisfy the
            formula """
        total = 0.0
        for assignment in product([False, True], repeat=self._num_vars):
            total += self.assignment_weight(assignment, ignore_truth)
        return total

    def assignment_weight(self, assignment: Iterable[bool], ignore_truth: bool =
    False) -> float:
        """ Get the weight given a specific assignment of variables. If
            ignore_truth is set to True this function will not return 0 when the
            truth value of the formula is False """
        if not ignore_truth and not self.assignment_truth(assignment):
            return 0.0
        total = 1.0
        for i, value in enumerate(assignment, 1):
            i = i if value else -i
            weight = self.get_weight(i)
            if weight is not None:
                total *= weight
        return total

    def assignment_truth(self, assignment: Iterable[bool]) -> bool:
        """ Check if the given assignment of variables makes the formula true
            """
        assignment = list(assignment)
        return all(self._clause_truth(clause, assignment) for clause in
        self.clauses)

    def vars(self) -> Iterable[int]:
        """ Iterate over positive variables used in this wCNF formula """
        yield from range(1, self._num_vars + 1)

    def signed_vars(self) -> Iterable[int]:
        """ Iterate over both positive and negative variables used in this wCNF
            formula """
        yield from range(-self._num_vars, self._num_vars + 1)

    def __len__(self) -> int:
        """ Get the number of variables in the formula """
        return self._num_vars
    
    def __str__(self) -> str:
        """ Convert this weighted CNF object to a standard CNF format text """
        return self.to_string()

    def _clause_truth(self, clause: list[int], assignment: list[bool]) -> bool:
        """ Check if the given clause holds, given assignment of variables """
        for i in clause:
            target = i > 0
            if assignment[abs(i) - 1] == target:
                return True
        return False