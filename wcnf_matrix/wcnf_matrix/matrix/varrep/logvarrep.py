
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
    
    def __init__(self, q: int):
        """ Constructor of a variable representation in the range 0,...,q-1 """
        super().__init__(q)
        self.vars = [BoolVar() for _ in range(int_log(q))]

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
    
    def substitute(self, mapping: dict[BoolVar, BoolVar]):
        self.vars = list(map(mapping, self.vars))

    def copy(self):
        other = LogVarRep(self.q)
        other.vars = self.vars.copy()
        return other
    
    def domain(self) -> Iterable[BoolVar]:
        return self.vars