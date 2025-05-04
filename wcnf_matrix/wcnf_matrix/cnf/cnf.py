
from typing import Iterable, Mapping, Any, Iterator
from itertools import chain, product
from .boolvar import BoolVar, SignedBoolVar

class CNF:
    """ A conjunctive normal form formula of boolean variables """

    def __init__(self, clauses: Iterable[Iterable[SignedBoolVar | BoolVar]] |
    None = None):
        """ Constructor, given some list of clauses in the formula """
        if clauses is None:
            self._clauses = []
        else:
            self._clauses = [list(SignedBoolVar.from_var(var) for var in clause)
            for clause in clauses]

    def __str__(self) -> str:
        """ String representation of the CNF formula """
        return "CNF(" + " ".join("(" + " ".join(str(x) for x in clause) + ")"
        for clause in self._clauses) + ")"

    def __repr__(self) -> str:
        """ Canonical representation """
        return f"{self.__class__.__name__}({self._clauses!r})"

    def __eq__(self, other: Any) -> bool:
        """ Check if two CNF formulae are the same. The order of clauses and
            terms within clauses does not matter, but other than this the
            clauses should be the same """
        if not isinstance(other, CNF):
            return False
        clauses = tuple(tuple(sorted(clause)) for clause in self._clauses)
        other_clauses = tuple(tuple(sorted(clause)) for clause in other._clauses)
        return clauses == other_clauses

    def __and__(self, other: "CNF") -> "CNF":
        """ Returns the conjunction of two CNF formulae """
        return CNF(chain(self._clauses, other._clauses))
    
    def __or__(self, other: "CNF") -> "CNF":
        """ Returns the disjunction of two CNF formulae. The number clauses will
            be the product of the number of clauses in the two separate formulae
            """
        return CNF(a + b for a, b in product(self._clauses, other._clauses))

    def __add__(self, other: "CNF") -> "CNF":
        """ Returns the conjunction of two CNF formulae """
        return CNF(chain(self._clauses, other._clauses))

    def __call__(self, values: Mapping[BoolVar, bool]) -> bool:
        """ Check if this CNF formula evaluates to true given the variable
            assignments """
        return self.truth_value(values)

    def add_clause(self, *clauses: Iterable[SignedBoolVar | BoolVar]):
        """ Append or multiple clauses to the CNF formula """
        for clause in clauses:
            self._clauses.append([SignedBoolVar.from_var(var) for var in
            clause])

    def subst(self, find: BoolVar, replace: BoolVar):
        """ Substitue all occurrences of the given variable in the CNF formula
            with another variable """
        self._clauses = [[SignedBoolVar(replace, x.value) if x.var == find else
        x for x in clause] for clause in self._clauses]

    def bulk_subst(self, var_map: dict[BoolVar, BoolVar]):
        """ Bulk substitute variables. This also allows for substitutions like
            {x: y, y: x} """
        self._clauses = [[SignedBoolVar(var_map[x.var], x.value) if x.var in
        var_map else x for x in clause] for clause in self._clauses]

    def copy(self) -> "CNF":
        """ Copy this formula. Keep in mind that the variables are still the
            same, but the clauses can be edited independently """
        return CNF(self._clauses)
    
    def truth_value(self, values: Mapping[BoolVar, bool]) -> bool:
        """ Check if this CNF formula evaluates to true given the variable
            assignments """
        return all(any(var.value == values[var.var] for var in clause) for
        clause in self._clauses)
    
    @property
    def clauses(self) -> Iterator[Iterable[SignedBoolVar]]:
        """ Iterate over all of the clauses of this CNF formula """
        yield from self._clauses