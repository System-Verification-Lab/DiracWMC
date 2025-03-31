
from typing import Any

name_index = 1

class SignedBoolVar:
    """ A boolean variable or its negation """

    def __init__(self, var: "BoolVar", value: bool = True):
        """ Constructor, given the boolean variable to turn into a signed
            boolean variable, and wether to negate the variable """
        self._var = var
        self._value = value

    def __str__(self) -> str:
        """ String representation is the name of the variable, with a "-" in
            front if it is negated """
        return f"{self._var}" if self._value else str(self._var)

    def __repr__(self) -> str:
        """ Canonical representation """
        return f"{self.__class__.__name__}({self._var!r}, {self._value!r})"

    def __neg__(self) -> "SignedBoolVar":
        """ Negate this signed variable """
        return SignedBoolVar(self._var, not self._value)
    
    def __pos__(self) -> "SignedBoolVar":
        """ Unary plus operator, which creates a copy of this signed nool var
            """
        return self.copy()
    
    def __eq__(self, other: Any) -> bool:
        """ Check if this signed boolean variable is equal to another """
        if not isinstance(other, SignedBoolVar):
            return False
        return self._var == other._var and self._value == other._value

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __lt__(self, other: "SignedBoolVar") -> bool:
        """ Comparison operator between the two underlying variables """
        return self._var < other._var
    
    def __le__(self, other: "SignedBoolVar") -> bool:
        """ Comparison operator between the two underlying variables """
        return self._var <= other._var
    
    def __gt__(self, other: "SignedBoolVar") -> bool:
        """ Comparison operator between the two underlying variables """
        return self._var > other._var
    
    def __ge__(self, other: "SignedBoolVar") -> bool:
        """ Comparison operator between the two underlying variables """
        return self._var >= other._var

    def copy(self) -> "SignedBoolVar":
        """ Create a copy of this object, without changing the variable referred
            to """
        return SignedBoolVar(self._var, self._value)

    @property
    def var(self) -> "BoolVar":
        """ Get the base boolean variable of this signed boolean variable """
        return self._var
    
    @property
    def value(self) -> bool:
        """ Returns if the boolean is positive or negative """
        return self._value

    @classmethod
    def from_var(self, var: "BoolVar | SignedBoolVar") -> "SignedBoolVar":
        """ Convert a boolean variable or signed boolean variable to a new
            signed boolean variable """
        if isinstance(var, BoolVar):
            return SignedBoolVar(var)
        return var.copy()

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
    
    def __neg__(self) -> SignedBoolVar:
        """ Negation of this boolean variable, which converts this boolean
            variable to a signed boolean variable with negative sign """
        return SignedBoolVar(self, False)

    def __pos__(self) -> SignedBoolVar:
        """ Unary plus operator, which converts this boolean variable to a
            signed boolean variable with positive sign """
        return SignedBoolVar(self, True)

    def __hash__(self) -> int:
        """ The hash of a boolean variable is the ID of the object """
        return id(self)