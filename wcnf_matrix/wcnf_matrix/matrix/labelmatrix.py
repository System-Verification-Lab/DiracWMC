
from __future__ import annotations
from typing import Iterable, Self, Iterator
from .abstractmatrix import AbstractMatrix
from .concretematrix import ConcreteMatrix
from ..reg import Reg

class LabelMatrix[Field, MatrixType: AbstractMatrix[Field]]:
    """ A matrix with annotated input and output dimensions. Annotations happen
        with registers """
    
    def __init__(self, mat: MatrixType, labels: Iterable[Reg]):
        """ Constructor, matrix to annotate and the annotations of the
            Hilbert subspaces (columns and rows respectively). The dimensions
            of the matrix need to be q ** len(labels), hence the matrix also
            needs to be square """
        self.mat = mat
        self.labels = list(labels)

    def __str__(self) -> str:
        """ String representation of a label matrix is given as (matrix, labels)
            """
        return f"({self.mat}, [" + ", ".join(str(label) for label in
        self.labels) + "])"

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

    def copy(self) -> Self:
        """ Create a copy of this label matrix """
        return LabelMatrix(self.mat.copy(), self.src_labels, self.dst_labels)

    def value(self) -> LabelMatrix[Field, ConcreteMatrix[Field]]:
        """ Convert the matrix to a concrete matrix with actual values stored in
            memory. Returns this new matrix, which still has labels """
        return LabelMatrix(self.mat.value(), self.labels)

    @classmethod
    def _make_compatible[Field, MatrixType: AbstractMatrix[Field]](cls,
    *matrices: LabelMatrix[Field, MatrixType]) -> Iterator[LabelMatrix[Field,
    MatrixType]]:
        """ Make one or more matrices compatible with each other by lining up
            Hilbert subspaces with the same label. Returns the compatible
            matrices """
        labels = set(sum([mat.labels for mat in matrices], []))
        return (mat._permutation(labels) for mat in matrices)
    
    def _permutation(self, labels: Iterable[Reg]) -> Self:
        """ Permute the Hilbert subspaces to the given sequence of labels. If a
            label is not present on this matrix, an identity operator will be
            permormed on this Hilbert subspace """
        labels = list(labels)
        src_labels = {label: i for i, label in enumerate(self.labels)}
        mat = self.mat.permutation(src_labels.get(label, -1) for label in
        labels)
        return LabelMatrix(mat, labels)