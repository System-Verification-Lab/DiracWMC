
from wcnf_matrix import (WCNFMatrix, ConcreteMatrix, Index, value, CNF,
WeightFunction, BoolVar)
from itertools import product
import pytest

@pytest.mark.parametrize("values", list(product(range(5), repeat=2)))
def test_bra_ket(values: tuple[int, int]):
    T = Index(5)
    assert (ConcreteMatrix.bra(T[values[0]]) * ConcreteMatrix.ket(T[values[1]])
    == value(WCNFMatrix.bra(T[values[0]]) * WCNFMatrix.ket(T[values[1]])))

def test_pauli_x():
    T = Index()
    a, b = BoolVar(), BoolVar()
    wf = WeightFunction([a, b])
    wf.fill(1.0)
    X = WCNFMatrix(T, CNF([[a, b], [-a, -b]]), wf, [a], [b])
    assert value(X) == ConcreteMatrix(T, [
        [0.0, 1.0],
        [1.0, 0.0],
    ])

def test_pauli_z():
    T = Index()
    a, z = BoolVar(), BoolVar()
    wf = WeightFunction([a, z])
    wf.fill(1.0)
    wf[z, True] = -1.0
    Z = WCNFMatrix(T, CNF([[z, -a], [-z, a]]), wf, [a], [a])
    assert value(Z) == ConcreteMatrix(T, [
        [1.0, 0.0],
        [0.0, -1.0],
    ])

def test_mul():
    T = Index()
    a, b = BoolVar(), BoolVar()
    wf = WeightFunction([a, b])
    wf.fill(1.0)
    I = WCNFMatrix(T, CNF(), wf, [a, b], [a, b])
    X = WCNFMatrix(T, CNF(), wf, [a, b], [b, a])
    assert value(X * I) == value(X) * value(I)

def test_mul_2():
    T = Index()
    a, b, z = BoolVar(), BoolVar(), BoolVar()
    wfx = WeightFunction([a, b])
    wfx.fill(1.0)
    wfz = WeightFunction([a, b, z])
    wfz.fill(1.0)
    wfz[z, True] = -1.0
    Z = WCNFMatrix(T, CNF([[z, -b], [-z, b]]), wfz, [a, b], [a, b])
    X = WCNFMatrix(T, CNF(), wfx, [a, b], [b, a])
    assert value(X * Z) == value(X) * value(Z)

def test_add():
    T = Index(3)
    a, b = BoolVar(), BoolVar()
    wf1 = WeightFunction([a, b])
    wf1.fill(1.0)
    cnf1 = CNF([[a, b], [-a, -b]])
    M1 = WCNFMatrix(T, cnf1, wf1, [a, b], [a, b])

    wf2 = WeightFunction([a, b])
    wf2.fill(1.0)
    wf2[a, True] = -2.0
    cnf2 = CNF()
    M2 = WCNFMatrix(T, cnf2, wf2, [a, b], [a, b])

    assert value(M1 + M2) == ConcreteMatrix(T, [
        [1.0, 0.0, 0.0],
        [0.0, 2.0, 0.0],
        [0.0, 0.0, -1.0],
    ])
