
from abc import ABC, abstractmethod
from typing import Iterator, Self

# Maximum display dimensions of the matrix in number of rows and columns
# respectively
MAX_DISPLAY_DIMS = (4, 4)

class AbstractMatrix[EntryType](ABC):
    """ An abstract matrix base class, used mainly for printing matrices """

    def __init__(self):
        """ Conustructor """
        pass
    
    def __getitem__(self, item: tuple[int, int]) -> EntryType:
        """ Get an entry from the matrix from a tuple (row, column). Indices may
            be negative to start from the back """
        if item[0] < 0:
            item = (item[0] + self.shape[0], item[1])
        if item[1] < 0:
            item = (item[0], item[1] + self.shape[1])
        return self.get_entry(*item)

    def __setitem__(self, item: tuple[int, int], value: EntryType):
        """ Set one of the entries in the matrix at location (row, column) to
            the given value. Indices may be negative to start from the back """
        self.set_entry(*item, value)

    def __str__(self) -> str:
        """ String representation of the matrix, which is abbreviated in the
            case there are too many columns/rows """
        def display_indices(size: int, max_size: int) -> list[int]:
            if size <= max_size:
                return list(range(size))
            return [*range(max_size // 2), -1, *range(size - (max_size + 1) //
            2, size)]
        rows = display_indices(self.shape[0], MAX_DISPLAY_DIMS[0])
        cols = display_indices(self.shape[1], MAX_DISPLAY_DIMS[1])
        def entry_string(row: int, col: int) -> str:
            if row < 0 and col < 0:
                return ""
            if row < 0 or col < 0:
                return "..."
            return str(self[row, col])
        strings = [[entry_string(r, c) for r in rows] for c in cols]
        pad_size = max(max(len(s) for s in r) for r in strings)
        return "[ " + "\n  ".join(" ".join(s.rjust(pad_size) for s in row) for
        row in strings) + "  ]"

    def __len__(self) -> int:
        """ Returns the total number of entries in the matrix """
        return self.shape[0] * self.shape[1]

    def __iter__(self) -> Iterator[EntryType]:
        """ Iterator over all of the entries in the matrix, row by row """
        for row in range(self.shape[0]):
            for col in range(self.shape[1]):
                yield self[row, col]

    def __mul__(self, other: Self | EntryType) -> Self:
        """ Multiply this matrix with another matrix or a scalar """
        if isinstance(other, AbstractMatrix):
            return self.__class__.product(self, other)
        return self.scalar_product(other)
    
    def __rmul__(self, other: EntryType) -> Self:
        """ Multiply this matrix with a scalar on the left """
        return self.scalar_product(other)

    def __add__(self, other: Self) -> Self:
        """ Add two matrices together """
        return self.__class__.sum(self, other)

    def __sub__(self, other: Self) -> Self:
        """ Subtract one matrix from another. This is only supported if -1 is
            valid for the entry type """
        return self.__class__.sum(self, other.scalar_product(-1))

    def __pow__(self, other: Self | int) -> Self:
        """ Exponentiate a matrix or compute the kronecker product of a matrix
            with another """
        if isinstance(other, int):
            return self.__class__.product(*((self,) * other))
        return self.__class__.kronecker(self, other)
    
    def __neg__(self) -> Self:
        """ Multiplication with -1 """
        return self.scalar_product(-1)
    
    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]:
        """ A tuple with the number of rows and columns respectively """
        pass

    @abstractmethod
    def get_entry(self, row: int, col: int) -> EntryType:
        """ Get an entry from the matrix at the given row and column """
        pass
    
    @abstractmethod
    def set_entry(self, row: int, col: int, value: EntryType):
        """ Set an entry in the matrix to the given value """
        pass
    
    @abstractmethod
    def scalar_product(self, factor: EntryType) -> Self:
        """ Get the scalar product of this matrix with some factor """
        pass

    def local_matrix(self, index: int, size: int, *, q: int = 2) -> Self:
        """ Assumes this matrix is square. Returns the matrix that is the
            kronecker product of I_(q^index), the current matrix, and I_(q^(size
            - index - log_q(cur_size))), where cur_size is the size of the
            current matrix. By default q is set to 2, it can be set to any value
            higher than 2. Note that the size of the current matrix should be a
            power of q exactly """
        if self.shape[0] != self.shape[1]:
            raise ValueError("To apply local_matrix, the matrix needs to be "
            f"square. The given matrix has shape {self.shape}")
        log_size = log_base(self.shape[0], q)
        if log_size == -1:
            raise ValueError(f"Cannot apply local_matrix on matrix with "
            f"dimension that is not a power of q = {q}. Given shape is "
            f"{self.shape}")
        
        return self.__class__.kronecker(
            self.__class__.identity(1 << index),
            self,
            self.__class__.identity(1 << (size - index - log_size))
        )

    @classmethod
    @abstractmethod
    def product(cls, *matrices: Self) -> Self:
        """ Get the matrix (dot) product of multiple matrices and return the new
            matrix """
        pass

    @classmethod
    @abstractmethod
    def kronecker(cls, *matrices: Self) -> Self:
        """ Get the kronecker product of multiple matrices and return the new
            matrix """
        pass
    
    @classmethod
    @abstractmethod
    def sum(cls, *matrices: Self) -> Self:
        """ Get the sum of multiple matrices and return the new matrix """
        pass
    
    @classmethod
    @abstractmethod
    def identity(cls, size: int) -> Self:
        """ Get the identity matrix with shape (size, size) """
        pass
    
    @classmethod
    @abstractmethod
    def zero(cls, shape: tuple[int, int]) -> Self:
        """ Get the zero matrix with the given shape """
        pass

def log_base(val: int, q: int):
    """ Calculate log_q(val). If val is not a perfect power of q this returns -1
        """
    if val <= 0:
        raise ValueError(f"Cannot calculate logarithm of non-positive value "
        f"{val}")
    total = 1
    while val > 1:
        if val % q != 0:
            return -1
        total += 1
        val //= q
    return total