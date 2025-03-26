
name_index = 1

class BoolVar:
    """ A boolean variable """

    def __init__(self, name: str | None = None):
        """ Constructor, which makes a new unique boolean variable, optionally
            with the given name """
        self._parent: BoolVar | None = None
        self._tree_size = 1
        if name is None:
            self._name = f"v{name_index}"
            name_index += 1
        else:
            self._name = name

    def __str__(self) -> str:
        """ String representation of the boolean variable keeps track of a
            global index to give a unique name, or gives the name of the
            variable if it has one """
        return self._root()._name

    def __eq__(self, other: "BoolVar") -> bool:
        """ Checks if two boolean variables are semantically the same """
        if isinstance(other, BoolVar):
            return self._root() == other._root()
        raise NotImplementedError

    def __hash__(self) -> int:
        """ Specialized hash function because two different objects are still
            equal if they have the same root """
        return hash(id(self._root()))

    def link(self, other: "BoolVar"):
        """ Make this and another boolean variable the semantically the same.
            The name of the new variable is the name of this boolean variable
            instance. If the other instance has a name, it is discarded """
        name = self.name
        self.__class__._combine(self, other)
        self.name = name

    @property
    def name(self) -> str:
        """ The name of the boolean variable. Note that it is possible two have
            two different variables with the same name. It is recommended to
            avoid this """
        return self._root()._name
    @name.setter
    def name(self, value: str):
        self._root()._name = value

    def _root(self) -> "BoolVar":
        """ Get the root node in the DSU of this boolean variable """
        if self._parent is None:
            return self
        self._parent = self._parent._root()
        return self._parent
    
    @classmethod
    def _combine(cls, x: "BoolVar", y: "BoolVar"):
        """ Combine the DSU trees of two boolean variables """
        x, y = x._root(), y._root()
        if x is y:
            return
        if x._tree_size < y._tree_size:
            x, y = y, x
        y._parent = x
        x._tree_size += y._tree_size