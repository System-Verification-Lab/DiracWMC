
from typing import Iterable, Mapping, Any
from .boolvar import BoolVar, SignedBoolVar

class CNF:
    """ A conjunctive normal form formula of boolean variables """

    def __init__(self, clauses: Iterable[Iterable[SignedBoolVar | BoolVar]] |
    None = None):
        """ Constructor, given some list of clauses in the formula """
        if clauses is None:
            self.clauses = []
        else:
            self.clauses = [list(SignedBoolVar.from_var(var) for var in clause)
            for clause in clauses]

    def __str__(self) -> str:
        """ String representation of the CNF formula """
        return "CNF(" + " ".join("(" + " ".join(str(x) for x in clause) + ")"
        for clause in self.clauses) + ")"

    def __repr__(self) -> str:
        """ Canonical representation """
        return f"{self.__class__.__name__}({self.clauses!r})"

    def __eq__(self, other: Any) -> bool:
        """ Check if two CNF formulae are the same. The order of clauses and
            terms within clauses does not matter, but other than this the
            clauses should be the same """
        if not isinstance(other, CNF):
            return False
        clauses = tuple(tuple(sorted(clause)) for clause in self.clauses)
        other_clauses = tuple(tuple(sorted(clause)) for clause in other.clauses)
        return clauses == other_clauses

    def subst(self, find: BoolVar, replace: BoolVar):
        """ Substitue all occurrences of the given variable in the CNF formula
            with another variable """
        self.clauses = [[SignedBoolVar(replace, x.value) if x.var == find else x
        for x in clause] for clause in self.clauses]

    def bulk_subst(self, var_map: dict[SignedBoolVar, SignedBoolVar]):
        """ Bulk substitute variables. This also allows for substitutions like
            {x: y, y: x} """
        self.clauses = [[var_map[x] if x in var_map else x for x in clause] for
        clause in self.clauses]

    def copy(self) -> "CNF":
        """ Copy this formula. Keep in mind that the variables are still the
            same, but the clauses can be edited independently """
        return CNF(self.clauses)
    
    def truth_value(self, values: Mapping[BoolVar, bool]) -> bool:
        # TODO
        ...