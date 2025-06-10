
from __future__ import annotations
from typing import Iterable, Iterator
from .varrep import VarRep
from ...cnf import CNF, BoolVar

def int_log(q: int) -> int:
    """ Get the log base 2 of q, rounded up to the nearest integer """
    return len(bin(q - 1)) - 2

def bin_rep(q: int) -> Iterator[bool]:
    """ Iterator over binary representation of a number q """
    return map(lambda x: x == "1", bin(q)[2:])

class LogVarRep(VarRep):
    """ Integer representation using a binary encoding, resulting in a
        logarithmic number of variables to represent a number """
    
    def __init__(self, q: int, vars: Iterable[BoolVar] | None = None):
        """ Constructor of a variable representation in the range 0,...,q-1. If
            vars is given, it has to have the length of num_vars """
        super().__init__(q, vars)
        if vars is None:
            self.vars = [BoolVar() for _ in range(int_log(q))]
        else:
            self.vars = list(vars)
            if len(self.vars) != int_log(q):
                raise RuntimeError(f"Number of variables passed to "
                f"{self.__class__.__name__} constructor must be {int_log(q)} "
                f"for q = {q}, instead got {len(self.vars)}")

    def __str__(self) -> str:
        """ String representation """
        return self.__repr__()

    def __repr__(self) -> str:
        """ Canonical representation """
        return f"{self.__class__.__name__}({self.q!r}, {self.vars!r})"

    def equals(self, number: int) -> CNF:
        cnf = CNF()
        for var in reversed(self.vars):
            if number & 1:
                cnf.add_clause([var])
            else:
                cnf.add_clause([-var])
            number >>= 1
        return cnf
    
    def less_than_q(self) -> CNF:
        ones: list[BoolVar] = []
        cnf = CNF()
        for var, is_one in zip(self.vars, bin_rep(self.q - 1)):
            if is_one:
                ones.append(var)
            else:
                cnf.add_clause([-var, *(-v for v in ones)])
        return cnf

    def equals_other(self, other: LogVarRep) -> CNF:
        cnf = CNF()
        for var, other_var in zip(self.vars, other.vars):
            cnf.add_clause([var, -other_var], [-var, other_var])
        return cnf
    
    def equals_other_to_var(self, other: LogVarRep, target_var: BoolVar) -> (
    tuple[CNF, list[BoolVar]]):
        assert self.q == other.q
        cnf = CNF()
        aux_vars = [BoolVar() for _ in range(self.vars)]
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
        other = LogVarRep(self.q)
        other.vars = self.vars.copy()
        return other
    
    def domain(self) -> Iterable[BoolVar]:
        return self.vars
    
    @classmethod
    def num_vars(self, q: int) -> int:
        return int_log(q)