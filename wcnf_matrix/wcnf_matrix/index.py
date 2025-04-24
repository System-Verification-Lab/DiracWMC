
class Index[Field]:
    """ Represents a Hilbert space for a q-state system, over some field given
        by a type of values """
    
    def __init__(self, q: int = 2, field: type[Field] = float):
        """ Constructor of a Hilbert space for a q-state system with the given
            field type """
        self.q = q
        self.field = field

    def __getitem__(self, element: int) -> "IndexBasisElement[Field]":
        """ Get one of the basis elements of this Hilbert space """
        return IndexBasisElement(self, element)

class IndexBasisElement[Field]:
    """ A basis element in some Hilbert space, which can be |0>, ..., |q-1> """

    def __init__(self, index: Index[Field], element: int):
        """ Constructor given the index (Hilbert space of the basis element) and
            the element, which can be 0, ..., q-1 """
        self.index = index
        self.element = element
        if not 0 <= element < self.index.q:
            raise ValueError(f"Element {element} is not in the standard basis "
            f"of a {self.index.q}-state Hilbert space")
