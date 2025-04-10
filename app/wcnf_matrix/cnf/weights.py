
from typing import Iterable, Iterator, Mapping, Callable
from itertools import chain, product
from functools import reduce
from .boolvar import BoolVar
from .cnf import CNF

class WeightFunction:
    """ A weight function mapping boolean variables to positive and negative
        weights. Weight functions can be combined for example by multiplying
        values on the overlap of the domains. Values of weights can be
        retrieved/changed by using wweight_func[var, True/False] """
    
    def __init__(self, domain: Iterable[BoolVar], *, weights: Mapping[BoolVar,
    tuple[float | None, float | None]] | None = None):
        """ Constructor, given the domain of variables, and optionally a map of
            variables to tuples of weights (negative, positive) """
        self._weights = {} if weights is None else dict(weights)
        for var in domain:
            self._weights.setdefault(var, (None, None))
        self._domain = set(domain)
        if any(var not in self._domain for var in self._weights):
            raise ValueError(f"Variable {var} not in domain")

    def __str__(self) -> str:
        """ String representation of the weight function """
        return ("WeightFunction(" + ", ".join(f"{var} => {value}" for var, value
        in self._weights.items()) + ")")

    def __repr__(self) -> str:
        """ Canonical representation """
        return (f"{self.__class__.__name__}({self._domain!r}, weights="
        f"{self._weights!r})")

    def __getitem__(self, item: tuple[BoolVar, bool]) -> float | None:
        """ Get the weight of the given variable with the given value """
        return self.get_weight(*item)
    
    def __setitem__(self, item: tuple[BoolVar, bool], weight: float | None):
        """ Set the weight of the given variable with the given value """
        self.set_weight(*item, weight)

    def __contains__(self, var: BoolVar) -> bool:
        """ Checks if the given variable is in the domain of the weight function
            """
        return var in self._domain

    def __iter__(self) -> Iterator[BoolVar]:
        """ Iterate over the domain of the weight function """
        yield from self._domain

    def __add__(self, other: "WeightFunction") -> "WeightFunction":
        """ Add two weight functions where they overlap. For variables where
            they do not overlap or one of the values is None, the values from
            one of the weight functions is chosen. """
        return self.combine(other, lambda x, y: x + y)

    def __mul__(self, other: "WeightFunction | float") -> "WeightFunction":
        """ Multiply two weight functions where they overlap. For variables
            where they do not overlap or one of the values is None, the values
            from one of the weight functions is chosen. If the value is a
            scalar, all weights are multiplied with this scalar """
        if isinstance(other, WeightFunction):
            return self.combine(other, lambda x, y: x * y)
        return self.apply(lambda v: None if v is None else v * other)
    
    def __rmul__(self, other: float) -> "WeightFunction":
        """ Multiply all weights with the given scalar """
        return self.__mul__(other)

    def __sub__(self, other: "WeightFunction") -> "WeightFunction":
        """ Subtract two weight functions where they overlap. For variables
            where they do not overlap or one of the values is None, the values
            from one of the weight functions is chosen. """
        return self.combine(other, lambda x, y: x - y)
    
    def __div__(self, other: "WeightFunction") -> "WeightFunction":
        """ Divide two weight functions where they overlap. For variables
            where they do not overlap or one of the values is None, the values
            from one of the weight functions is chosen. """
        return self.combine(other, lambda x, y: x / y)

    def __eq__(self, other: "WeightFunction") -> bool:
        """ Check if two weight functions are equal, i.e., their domains and all
            of their values are equal """
        return self.compare(other, lambda x, y: x == y)
    
    def __ne__(self, other: "WeightFunction") -> bool:
        """ Check if two weight functions are unequal, either because they have
            different domains or because their values differ """
        return not (self == other)

    def __abs__(self) -> "WeightFunction":
        """ Convert all weights to their absolute value and return the resulting
            weight function """
        return self.apply(abs)

    def __call__(self, cnf: CNF) -> float:
        """ The weighted model count of the given formula with respect to this
            weight function. Calculated using brute force """
        return self.model_count(cnf)

    def compare(self, other: "WeightFunction", func: Callable[[float | None,
    float | None], bool], *, same_domain: bool = False) -> bool:
        """ Compare two weight functions given a compare function. If the
            function returns True on all variable/value pairs that are in the
            domains of both functions. Optionally it can be required that both
            weight functions have the same domain """
        if same_domain and self.domain != other.domain:
            return False
        return all(func(self[var, val], other[var, val]) for var, val in
        product(self.overlap(other), (True, False)))

    def overlap(self, other: "WeightFunction") -> Iterator[BoolVar]:
        """ Get the overlap of domains of two weight functions """
        yield from filter(lambda var: var in other.domain, self.domain)

    def subst(self, find: BoolVar, replace: BoolVar):
        """ Substitute the given variable in the domain with another variable.
            An error is thrown if the substitution results in multiple of the
            same variable in the domain """
        if find == replace:
            return
        if replace in self._domain:
            raise ValueError(f"Variable {replace} is already in domain")
        self._domain.remove(find)
        self._domain.add(replace)
        self._weights[replace] = self._weights[find]
        self._weights.pop(find)

    def bulk_subst(self, var_map: Mapping[BoolVar, BoolVar]):
        """ Bulk substitute variables. This also allows for substitutions like
            {x: y, y: x}. If the substitution results in multiple of the same
            variable in the domain, or if the variables to substitute are not in
            the domain, an error is thrown """
        var_map = dict(var_map)
        # Determine resulting domain and check if there are not duplicates
        for var in var_map.keys():
            self.domain.remove(var)
        for var in var_map.values():
            if var in self.domain:
                raise ValueError(f"Duplicate variable {var} after substitution")
            self.domain.add(var)
        # Add new values to separate dict
        new_values: dict[BoolVar, tuple[float | None, float | None]] = {}
        for src, dst in var_map.items():
            new_values[dst] = self._weights[src]
        # Remove keys because they are changed
        for var in var_map.keys():
            self._weights.pop(var)
        # Add separate dict to existing
        for var, val in new_values.items():
            self._weights[var] = val

    def copy(self) -> "WeightFunction":
        """ Copy this weight function. Keep in mind that the variables
            themselves stay the same, but the weights can be modified
            independently """
        return WeightFunction(self._domain.copy(), weights=self._weights)

    def get_weight(self, var: BoolVar, value: bool) -> float | None:
        """ Get the weight of the given variable with the given value. Throw a
            KeyError if the variable is not in the domain """
        if var not in self._weights:
            raise KeyError(f"Variable {var} not in domain of weight function")
        return self._weights[var][value]
    
    def set_weight(self, var: BoolVar, value: bool, weight: float | None):
        """ Set the weight of the given variable with the given value. Throw a
            KeyError if the variable is not in the domain """
        if var not in self._domain:
            raise KeyError(f"Variable {var} not in domain of weight function")
        cur = self._weights[var]
        cur = (cur[0], weight) if value else (weight, cur[1])
        self._weights[var] = cur

    def clear(self):
        """ Clear all weights of the weight function to None """
        self.fill(None)

    def fill(self, weight: float | None):
        """ Set all positive and negative weights to the given value """
        for var in self._domain:
            self.set_weight(var, False, weight)
            self.set_weight(var, True, weight)
    
    def fill_missing(self, value: float | None):
        """ Set all missing (None) positive and negative weights to the given
            value """
        if value is None:
            return
        for var in self._domain:
            old = self._weights[var]
            self._weights[var] = (value if old[0] is None else old[0], value if
            old[1] is None else old[1])

    def items(self) -> Iterator[tuple[BoolVar, bool, float | None]]:
        """ Get an iterator over all of the variable and value weight
            assignments """
        for var, (neg, pos) in self._weights.items():
            yield (var, False, neg)
            yield (var, True, pos)

    def apply(self, func: Callable[[float | None], float | None]) -> (
    "WeightFunction"):
        """ Apply the given function to all weights and return the resulting
            weight function """
        return WeightFunction(self._domain, weights={var: (func(neg), func(pos))
        for var, (neg, pos) in self._weights.items()})

    def combine(self, other: "WeightFunction", func: Callable[[float, float],
    float]) -> "WeightFunction":
        """ Combine two weight functions and apply the given function when both
            weight functions have the same variable in their domains and neither
            assigns None. If one of them does assign None, the weight is taken
            from the other weight function """
        result = WeightFunction(self.domain.union(other.domain))
        for var, value, weight in chain(self.items(), other.items()):
            cur_weight = result.get_weight(var, value)
            if cur_weight is None:
                result.set_weight(var, value, weight)
            else:
                result.set_weight(var, value, func(weight, cur_weight))
        return result

    def model_count(self, cnf: CNF) -> float:
        """ The weighted model count of the given formula with respect to this
            weight function. Calculated using brute force """
        return sum(self._mapping_weight(mapping) for mapping in
        self._var_mappings() if cnf(mapping))

    @property
    def domain(self) -> set[BoolVar]:
        """ The domain of the weight function as a tuple of variables """
        return self._domain

    def _var_mappings(self) -> Iterator[Mapping[BoolVar, bool]]:
        """ Get an iterator over all possible variable assignment mappings given
            the domain of the weight function """
        var_list = tuple(self.domain)
        for assignment in product((False, True), repeat=len(var_list)):
            yield {var: value for var, value in zip(var_list, assignment)}

    def _mapping_weight(self, mapping: Mapping[BoolVar, bool]) -> float:
        """ Get the weight of the given variable assignment mapping """
        return reduce(lambda x, y: x * y, (self.get_weight(var, mapping[var])
        for var in self.domain), 1.0)