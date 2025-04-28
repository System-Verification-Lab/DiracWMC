
from __future__ import annotations
from .abstractmatrix import AbstractMatrix
from ..reg import Reg
from typing import Iterable, Any, Self

class LabelMatrix[Field, MatrixType: AbstractMatrix[Field]]:
    """ A matrix with annotated input and output dimensions. Annotations happen
        with registers """
    
    def __init__(self, mat: MatrixType, src_labels: Iterable[Reg], dst_labels:
    Iterable[Reg] | None = None):
        """ Constructor, matrix to annotate and the annotations of the source
            and destination dimensions (columns and rows respectively). If
            dst_labels is not given or None, it is set to the same value as
            src_labels. The dimensions of the matrix need to be (q **
            len(dst_labels), q ** len(src_labels)) """
        src_labels = list(src_labels)
        dst_labels = src_labels if dst_labels is None else list(dst_labels)
        self.src_labels = src_labels
        self.dst_labels = dst_labels
        self.mat = mat

    def __mul__(self, other: LabelMatrix[Field, MatrixType] | Field) -> Self:
        """ Multiply one label matrix with another, or multiply this label
            matrix with a scalar, and return the result """
        if not isinstance(other, LabelMatrix):
            out = self.copy()
            out.mat *= other
            return out
        ...

    def __rmul__(self, other: Field) -> Self:
        """ Multiply this label matrix with a scalar on the left, and return the
            result """
        return self * other

    def __add__(self, other: LabelMatrix[Field, MatrixType]) -> Self:
        """ Add one label matrix to another and return the result """
        ...

    def copy(self) -> Self:
        """ Create a copy of this label matrix """
        return LabelMatrix(self.mat.copy(), self.src_labels, self.dst_labels)

    