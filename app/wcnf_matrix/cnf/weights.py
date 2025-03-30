
from typing import Iterable
from .boolvar import BoolVar

class WeightFunction:
    """ A weight function mapping boolean variables to positive and negative
        weights """
    
    def __init__(self, domain: Iterable[BoolVar]):
        """ Constructor, given the domain of variables """
        self._domain = set(domain)
        self._weights: dict[BoolVar, tuple[float | None, float | None]] = {}

    def __getitem__(self, item: tuple[BoolVar, bool]) -> float | None:
        """ Get the weight of the given variable with the given value """
        return self.get_weight(*item)
    
    def __setitem__(self, item: tuple[BoolVar, bool], weight: float | None):
        """ Set the weight of the given variable with the given value """
        self.set_weight(*item, weight)

    def __add__(self, other: "WeightFunction") -> "WeightFunction":
        """ Add two weight functions where they overlap. If  """

    def subst(self, find: BoolVar, replace: BoolVar):
        """ Substitute the given variable in the domain with another variable.
            An error is thrown if the substitution results in multiple of the
            same variable in the domain """
        if find == replace:
            return
        if replace in self._domain:
            raise ValueError(f"Variable {replace} is already in domain")
        self._weights[replace] = self._weights[find]
        self._weights.pop(find)

    def bulk_subst(self, var_map: dict[BoolVar, BoolVar]):
        """ Bulk substitute variables. This also allows for substitutions like
            {x: y, y: x}. If the substitution results in multiple of the same
            variable in the domain, and error is thrown """
        new_weights: dict[BoolVar, tuple[float | None, float | None]] = {}
        for find, replace in var_map.items():
            if replace in new_weights:
                raise ValueError(f"Variable {replace} is already in domain")
            new_weights[replace] = self._weights[find]
        replaced_vars = set(var_map.keys())
        for var, value in self._weights.items():
            if var in replaced_vars:
                continue
            if var in new_weights:
                raise ValueError(f"Variable {var} is already in domain")
            new_weights[var] = value
        self._weights = new_weights

    def copy(self) -> "WeightFunction":
        """ Copy this weight function. Keep in mind that the variables
            themselves stay the same, but the weights can be modified
            independently """
        wf = WeightFunction(self._domain.copy())
        wf._weights = self._weights.copy()
        return wf

    def get_weight(self, var: BoolVar, value: bool) -> float | None:
        """ Get the weight of the given variable with the given value """
        return self._weights.get(var, (None, None))[value]
    
    def set_weight(self, var: BoolVar, value: bool, weight: float | None):
        """ Set the weight of the given variable with the given value """
        cur = self._weights.get(var, (None, None))
        cur = (cur[0], weight) if value else (weight, cur[1])
        self._weights[var] = cur

    def fill(self, weight: float):
        """ Set all positive and negative weights to the given value """
        for var in self._domain:
            self.set_weight(var, False, weight)
            self.set_weight(var, True, weight)
    
    def fill_missing(self, value: float):
        """ Set all missing (None) positive and negative weights to the given
            value """
        for var in self._domain:
            old = self._weights[var]
            self._weights[var] = (value if old[0] is None else old, value if
            old[1] is None else old)