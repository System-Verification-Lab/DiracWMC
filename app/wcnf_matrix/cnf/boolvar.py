
from typing import Any

name_index = 1

class BoolVar:
    """ A boolean variable """

    def __init__(self, name: str | None = None):
        """ Constructor, which makes a new unique boolean variable, optionally
            with the given name """
        global name_index
        self._parent: BoolVar | None = None
        self._index = name_index
        name_index += 1
        self.name = f"v{self._index}" if name is None else name

    def __str__(self) -> str:
        """ String representation is the name of the variable """
        return self.name

    def __repr__(self) -> str:
        """ Canonical representation """
        return f"{self.__class__.__name__}({self.name!r})"

    def __eq__(self, other: Any) -> bool:
        """ Checks if two boolean variables are the same """
        return self is other

    def __ne__(self, other: Any) -> bool:
        """ Checks if two boolean variables are not the same """
        return self is not other

    def __lt__(self, other: Any) -> bool:
        """ Compare two boolean variables. Used for sorting variables by the
            time they were initialized """
        if not isinstance(other, BoolVar):
            raise NotImplementedError
        return self._index < other._index

    def __le__(self, other: "BoolVar") -> bool:
        """ Compare two boolean variables. Used for sorting variables by the
            time they were initialized """
        if not isinstance(other, BoolVar):
            raise NotImplementedError
        return self._index <= other._index
    
    def __gt__(self, other: "BoolVar") -> bool:
        """ Compare two boolean variables. Used for sorting variables by the
            time they were initialized """
        if not isinstance(other, BoolVar):
            raise NotImplementedError
        return self._index > other._index
    
    def __ge__(self, other: "BoolVar") -> bool:
        """ Compare two boolean variables. Used for sorting variables by the
            time they were initialized """
        if not isinstance(other, BoolVar):
            raise NotImplementedError
        return self._index >= other._index
    
    def __hash__(self) -> int:
        """ The hash of a boolean variable is the ID of the object """
        return id(self)