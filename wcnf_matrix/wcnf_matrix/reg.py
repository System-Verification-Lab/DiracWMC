
from .index import Index

class Reg[Field]:
    """ A register in a Hilbert space """

    def __init__(self, index: Index[Field]):
        """ Constructor, given the index (Hilbert space) of the register """
        self.index = index