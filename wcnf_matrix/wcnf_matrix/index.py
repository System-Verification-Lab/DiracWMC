
class Index[Field]:
    """ Represents a Hilbert space for a q-state system, over some field given
        by a type of values """
    
    def __init__(self, q: int = 2, field: type[Field] = float):
        """ Constructor of a Hilbert space for a q-state system with the given
            field type """
        self.q = q
        self.field = field
