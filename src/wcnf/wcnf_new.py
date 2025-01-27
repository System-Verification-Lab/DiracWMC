""" Contains a definition for weighted CNF formula objects """

from typing import Iterable

class WeightedCNF:
    """ Represents a weighted CNF formula. Variables are 1-indexed in clauses
        and weights lists """

    def __init__(self, num_vars: int):
        """ Constructor, given the number of variables """
        self._num_vars = num_vars
        self._weights: list[float | None] = [None] * (num_vars * 2 + 1)
        self._clauses: list[list[int]] = []

    def set_weight(self, var: int, weight: float | None):
        """ Set the weight of a variable. If variable is negative, set the
            weight of the negation """
        assert var != 0 and abs(var) <= self._num_vars
        self._weights[var + self._num_vars] = weight

    def get_weight(self, var: int) -> float | None:
        """ Get the weight of a variable given its truth value (sign) """
        assert var != 0 and abs(var) <= self._num_vars
        return self._weights[var + self._num_vars]

    def add_missing_weights(self):
        """ Add any weights that are not set. If a x is set but -x is not (or
            vice versa), then weight(-x) = 1 - weight(x). If neither x nor -x is
            set, then weight(-x) = weight(x) = 0.5 """
        for i in self.vars:
            has_pos = self.get_weight(i) is not None
            has_neg = self.get_weight(-i) is not None
            if not has_pos and not has_neg:
                self.set_weight(i, 0.5)
                self.set_weight(i, 0.5)
            elif not has_pos:
                self.set_weight(i, 1 - self.get_weight(-i))
            elif not has_neg:
                self.set_weight(-i, 1 - self.get_weight(i))

    @property
    def vars(self) -> Iterable[int]:
        """ Returns an iterable over all (positive) variables """
        yield from range(1, self._num_vars + 1)

    def __len__(self) -> int:
        """ Get the number of clauses in the formula """
        return len(self._clauses)
    
    def __getitem__(self, i: int) -> list[int]:
        """ Get a reference the i'th clause """
        return self._clauses[i]
    
    def __setitem__(self, i: int, clause: list[int]):
        """ Set the i'th clause """
        self._clauses[i] = clause

    