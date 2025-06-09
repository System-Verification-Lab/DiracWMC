
from abc import abstractmethod
from ...cnf import CNF, BoolVar
from typing import Self, Iterable

class VarRep:
    """ Base class of integer representations using Boolean variables """

    def __init__(self, q: int):
        """ Constructor of a variable representation in the range 0,...,q-1 """
        self.q = q

    @abstractmethod
    def equals(self, number: int) -> CNF:
        """ Returns a CNF formula that checks if the var representation is equal
            to the given number. Number should be in the range 0,...,q-1 """
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
        """ Get all variables used in the representation """
        pass