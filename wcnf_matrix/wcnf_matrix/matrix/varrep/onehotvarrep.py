
from __future__ import annotations
from typing import Iterable
from .varrep import VarRep
from ...cnf import CNF, BoolVar
from itertools import product

class OneHotVarRep(VarRep):
    """ Integer representation using a one-hot, resulting in a linear number of
        variables to represent a number """
    
    def __init__(self, q: int, vars: Iterable[BoolVar] | None = None):
        """ Constructor of a variable representation in the range 0,...,q-1. If
            vars is given, it has to have the length of num_vars """
        super().__init__(q, vars)
        if vars is None:
            self.vars = [BoolVar() for _ in range(q)]
        else:
            self.vars = list(vars)
            if len(self.vars) != q:
                raise RuntimeError(f"Number of variables passed to "
                f"{self.__class__.__name__} constructor must be {q} for q "
                f"= {q}, instead got {len(self.vars)}")

    def __str__(self) -> str:
        """ String representation """
        return self.__repr__()

    def __repr__(self) -> str:
        """ Canonical representation """
        return f"{self.__class__.__name__}({self.q!r}, {self.vars!r})"

    def equals(self, number: int) -> CNF:
        cnf = CNF()
        for i, var in enumerate(self.vars):
            if i == number:
                cnf.add_clause([var])
            else:
                cnf.add_clause([-var])
        return cnf
    
    def less_than_q(self) -> CNF:
        cnf = CNF()
        cnf.add_clause(self.vars)
        for i, j in product(self.vars, self.vars):
            if i != j:
                cnf.add_clause([-i, -j])
        return cnf

    def equals_other(self, other: OneHotVarRep) -> CNF:
        assert self.q == other.q
        cnf = CNF()
        for var, other_var in zip(self.vars, other.vars):
            cnf.add_clause([var, -other_var], [-var, other_var])
        return cnf
    
    def equals_other_to_var(self, other: OneHotVarRep, target_var: BoolVar) -> (
    tuple[CNF, list[BoolVar]]):
        assert self.q == other.q
        cnf = CNF()
        aux_vars = [BoolVar() for _ in self.vars]
        # Introduce formulae a <-> (x <-> y)
        for var, other_var, aux_var in zip(self.vars, other.vars, aux_vars):
            cnf.add_clause(
                [-aux_var, var, -other_var],
                [-aux_var, -var, other_var],
                [aux_var, var, other_var],
                [aux_var, -var, -other_var],
            )
        cnf.add_clause([target_var, *(-av for av in aux_vars)])
        cnf.add_clause(*([-target_var, av] for av in aux_vars))
        return cnf, aux_vars

    def substitute(self, mapping: dict[BoolVar, BoolVar]):
        m = lambda x: mapping.get(x, x)
        self.vars = list(map(m, self.vars))

    def copy(self):
        return OneHotVarRep(self.q, self.vars.copy())
    
    def domain(self) -> Iterable[BoolVar]:
        return self.vars
    
    @classmethod
    def num_vars(self, q: int) -> int:
        return q