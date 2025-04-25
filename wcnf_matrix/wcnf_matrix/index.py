
from typing import Any, Iterator

class Index[Field]:
    """ Represents a Hilbert space for a q-state system, over some field given
        by a type of values """

    def __init__(self, q: int = 2, field: type[Field] = float):
        """ Constructor of a Hilbert space for a q-state system with the given
            field type """
        self.q = q
        self.field = field

    def __str__(self) -> str:
        """ String representation of the index for debugging """
        return "Index" + str(id(self) % 10000).zfill(4)

    def __getitem__(self, value: int) -> "IndexBasisElement[Field]":
        """ Get one of the basis elements of this Hilbert space """
        return IndexBasisElement(self, value)

class IndexBasisElement[Field]:
    """ A basis element in some Hilbert space, which can be |0>, ..., |q-1> """

    def __init__(self, index: Index[Field], value: int):
        """ Constructor given the index (Hilbert space of the basis element) and
            the element, which can be 0, ..., q-1 """
        self.index = index
        self.value = value
        if not 0 <= value < self.index.q:
            raise ValueError(f"Element |{value}> is not in the standard basis "
            f"of a {self.index.q}-state Hilbert space")

    def __str__(self) -> str:
        """ String representation of the basis element for debugging """
        return f"{self.index}[{self.value}]"

    def __eq__(self, other: Any) -> bool:
        """ Two basis elements are equal if their indices and values are the
            same """
        if not isinstance(other, IndexBasisElement):
            return False
        return self.index == other.index and self.value == other.value

    @property
    def field(self) -> type[Field]:
        """ The field of the Hilbert space this element is in """
        return self.index.field

def uset[Field](index: Index[Field]) -> Iterator[IndexBasisElement[Field]]:
    """ Get the set of basis elements of the given index """
    return (index[i] for i in range(index.q))