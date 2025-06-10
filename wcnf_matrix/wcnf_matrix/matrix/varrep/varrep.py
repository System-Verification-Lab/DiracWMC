
from abc import abstractmethod
from ...cnf import CNF, BoolVar
from typing import Self, Iterable

class VarRep:
    """ Base class of integer representations using Boolean variables """

    def __init__(self, q: int, vars: Iterable[BoolVar] | None = None):
        """ Constructor of a variable representation in the range 0,...,q-1. If
            vars is given, it has to have the length of num_vars """
        self.q = q

    @abstractmethod
    def equals(self, number: int) -> CNF:
        """ Returns a CNF formula that checks if the var representation is equal
            to the given number. Number should be in the range 0,...,q-1. This
            formula also checks if the representation is valid """
        pass

    @abstractmethod
    def less_than_q(self) -> CNF:
        """ Get a CNF formula for the number being represented being less than
            the base number q. This formula also makes sure the formula
            represents exactly one value """
        pass

    @abstractmethod
    def equals_other(self, other: Self) -> CNF:
        """ Get a CNF formula that represents the value of this variable
            representation being equal to that of another. This formula does not
            check if either value is valid """
        pass

    @abstractmethod
    def equals_other_to_var(self, other: Self, target_var: BoolVar) -> tuple[
    CNF, list[BoolVar]]:
        """ Similar to equals_other, but returns the formula var <=> (self <=>
            other) instead of self <=> other. This formula does not check if
            either value is valid. This function may introduce auxiliary
            variables, which are returned as a list in the second argument of
            the return value """
        pass

    @abstractmethod
    def substitute(self, mapping: dict[BoolVar, BoolVar]):
        """ Substitute variables in this variable representation """
        pass

    @abstractmethod
    def copy(self) -> Self:
        """ Copy the variable representation, leaving the variables used the
            same """
        pass

    @abstractmethod
    def domain(self) -> Iterable[BoolVar]:
        """ Get all variables used in the representation. Variables are ordered
            the same way, such that two variable representations can be compared
            """
        pass

    @classmethod
    @abstractmethod
    def num_vars(self, q: int) -> int:
        """ Returns the number of variables used for a representation of a
            number in the range 0,...,q-1 """
        pass