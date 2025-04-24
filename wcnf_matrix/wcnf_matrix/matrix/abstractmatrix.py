
from abc import ABC, abstractmethod
from typing import Self
from ..index import Index, IndexBasisElement

class AbstractMatrix[Field](ABC):
    """ Abstract definition of a matrix, with operations for creating bras and
        kets, addition, multiplication, etc. """
    
    def __init__(self, index: Index):
        """ Constructor with the Hilbert space the matrix operates on """
        self._index = index

    @abstractmethod
    def __add__(cls, other: Self) -> Self:
        """ Add two matrices together and return the result """
        pass

    @classmethod
    @abstractmethod
    def bra(cls, element: IndexBasisElement[Field]):
        """ Row vector of a basis element """
        pass

    @classmethod
    @abstractmethod
    def ket(cls, element: IndexBasisElement[Field]):
        """ Column vector of a basis element """
        pass