
from .index import Index

creation_index = 0

class Reg[Field]:
    """ A register in a Hilbert space """

    def __init__(self, index: Index[Field]):
        """ Constructor, given the index (Hilbert space) of the register """
        self.index = index
        global creation_index
        self._creation_index = creation_index
        creation_index += 1

    def __str__(self) -> str:
        """ String representation fot debugging """
        return f"reg{self._creation_index}"