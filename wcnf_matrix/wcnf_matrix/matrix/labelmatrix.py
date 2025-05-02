
from __future__ import annotations
from typing import Iterable, Self, Iterator, Any
from .abstractmatrix import AbstractMatrix
from .concretematrix import ConcreteMatrix
from ..reg import Reg

class LabelMatrix[Field, MatrixType: AbstractMatrix[Field]]:
    """ A matrix with annotated input and output dimensions. Annotations happen
        with registers """
    
    def __init__(self, mat: MatrixType, labels: Iterable[Reg]):
        """ Constructor, matrix to annotate and the annotations of the
            Hilbert subspaces (columns and rows respectively). The dimensions
            of the matrix need to be q ** len(labels). Optionally one of the
            dimensions can be 1, so that the matrix is either a row or column
            vector, or a square matrix """
        self.mat = mat
        if not self._can_be_labelled(mat):
            raise ValueError(f"Matrix with shape {mat.shape} and base q = "
            f"{mat.index.q} cannot be labelled")
        labels = list(labels)
        labels_length = max(self._exact_log(self.mat.shape[i], self.mat.index.q)
        for i in (0, 1))
        if len(labels) != labels_length:
            raise ValueError(f"Number of labels provided {len(labels)} "
            f"does not match required amount {labels_length}")
        self.labels = labels

    def __str__(self) -> str:
        """ String representation of a label matrix is given as (matrix, labels)
            """
        return f"{self.mat} | (" + ", ".join(str(label) for label in
        self.labels) + ")"

    def __mul__(self, other: LabelMatrix[Field, MatrixType] | Field) -> Self:
        """ Multiply one label matrix with another, or multiply this label
            matrix with a scalar, and return the result """
        if not isinstance(other, LabelMatrix):
            out = self.copy()
            out.mat *= other
            return out
        left, right = self.__class__._make_compatible(self, other)
        return LabelMatrix(left.mat * right.mat, left.labels)

    def __rmul__(self, other: Field) -> Self:
        """ Multiply this label matrix with a scalar on the left, and return the
            result """
        return self * other

    def __add__(self, other: LabelMatrix[Field, MatrixType]) -> Self:
        """ Add one label matrix to another and return the result """
        left, right = self.__class__._make_compatible(self, other)
        return LabelMatrix(left.mat + right.mat, right.labels)

    def __eq__(self, other: Any) -> bool:
        """ Check if this LabelMatrix is equal to another object, which will
            only return True if the other object is also a LabelMatrix. In this
            case the labels of the matrices are reordered and possibly extended
            before the matrices are compared """
        if not isinstance(other, LabelMatrix):
            return False
        left, right = LabelMatrix._make_compatible(self, other)
        return left.mat == right.mat

    def copy(self) -> Self:
        """ Create a copy of this label matrix """
        return LabelMatrix(self.mat.copy(), self.src_labels, self.dst_labels)

    def value(self) -> LabelMatrix[Field, ConcreteMatrix[Field]]:
        """ Convert the matrix to a concrete matrix with actual values stored in
            memory. Returns this new matrix, which still has labels """
        return LabelMatrix(self.mat.value(), self.labels)

    def permutation(self, labels: Iterable[Reg]) -> Self:
        """ Permute the Hilbert subspaces to the given sequence of labels. If a
            label is not present on this matrix, an identity operator will be
            permormed on this Hilbert subspace. This method accounts for square
            matrices, row vectors, and column vectors separately """
        labels = list(labels)
        src_labels = {label: i for i, label in enumerate(self.labels)}
        indices = [src_labels.get(label, -1) for label in labels]
        if self._is_row_vector():
            mat = self.mat.permutation(indices, [])
        elif self._is_column_vector():
            mat = self.mat.permutation([], indices)
        else:
            mat = self.mat.permutation(indices)
        return LabelMatrix(mat, labels)

    @classmethod
    def _make_compatible[Field, MatrixType: AbstractMatrix[Field]](cls,
    *matrices: LabelMatrix[Field, MatrixType]) -> Iterator[LabelMatrix[Field,
    MatrixType]]:
        """ Make one or more matrices compatible with each other by lining up
            Hilbert subspaces with the same label. Returns the compatible
            matrices """
        labels = set(sum([mat.labels for mat in matrices], []))
        return (mat.permutation(labels) for mat in matrices)
    
    def _is_row_vector(self) -> bool:
        """ Check if the matrix stored in this label matrix is a row vector """
        return self.mat.shape[0] == 1

    def _is_column_vector(self) -> bool:
        """ Check if the matrix stored in this label matrix is a column vector
            """
        return self.mat.shape[1] == 1

    def _can_be_labelled(self, mat: MatrixType) -> bool:
        """ Check if the given matrix is square or a row/column vector, and has
            compatible dimensions """
        q = mat.index.q
        try:
            log_shape = self._exact_log(mat.shape[0], q), self._exact_log(
            mat.shape[1], q)
        except:
            return False
        # Square matrix
        if log_shape[0] != 0 and log_shape[1] != 0:
            return log_shape[0] == log_shape[1]
        # Row/column vector
        return True
    
    def _exact_log(self, val: int, q: int) -> int:
        """ Determine the log base q of a value. If the value is not a power of
            q, this throws a ValueError """
        out = 0
        while val > 1:
            if val % q != 0:
                raise ValueError(f"Value {val} is not a power of q = {q}")
            val //= q
            out += 1
        return out