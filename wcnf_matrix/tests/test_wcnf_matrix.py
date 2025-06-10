
from wcnf_matrix import (WCNFMatrix, ConcreteMatrix, Index, value, CNF,
WeightFunction, BoolVar, get_var_rep_type)
from itertools import product
import pytest

@pytest.mark.parametrize("values", list(product(range(5), repeat=2)))
def test_bra_ket(values: tuple[int, int]):
    T = Index(5)
    assert (ConcreteMatrix.bra(T[values[0]]) * ConcreteMatrix.ket(T[values[1]])
    == value(WCNFMatrix.bra(T[values[0]]) * WCNFMatrix.ket(T[values[1]])))

def test_pauli_x():
    var_rep = get_var_rep_type()
    T = Index()
    q = T.q
    a, b = BoolVar(), BoolVar()
    wf = WeightFunction([a, b])
    wf.fill(1.0)
    X = WCNFMatrix(T, CNF([[a, b], [-a, -b]]), wf, [var_rep(q, [a])],
    [var_rep(q, [b])])
    assert value(X) == ConcreteMatrix(T, [
        [0.0, 1.0],
        [1.0, 0.0],
    ])

def test_pauli_z():
    var_rep = get_var_rep_type()
    T = Index()
    q = T.q
    a, z = BoolVar(), BoolVar()
    wf = WeightFunction([a, z])
    wf.fill(1.0)
    wf[z, True] = -1.0
    Z = WCNFMatrix(T, CNF([[z, -a], [-z, a]]), wf, [var_rep(q, [a])],
    [var_rep(q, [a])])
    assert value(Z) == ConcreteMatrix(T, [
        [1.0, 0.0],
        [0.0, -1.0],
    ])

def test_mul():
    var_rep = get_var_rep_type()
    T = Index()
    q = T.q
    a, b = BoolVar(), BoolVar()
    wf = WeightFunction([a, b])
    wf.fill(1.0)
    ab = [var_rep(q, [a]), var_rep(q, [b])]
    ba = [var_rep(q, [b]), var_rep(q, [a])]
    I = WCNFMatrix(T, CNF(), wf, ab, ab)
    X = WCNFMatrix(T, CNF(), wf, ab, ba)
    assert value(X * I) == value(X) * value(I)

def test_mul_2():
    var_rep = get_var_rep_type()
    T = Index()
    q = T.q
    a, b, z = BoolVar(), BoolVar(), BoolVar()
    wfx = WeightFunction([a, b])
    wfx.fill(1.0)
    wfz = WeightFunction([a, b, z])
    wfz.fill(1.0)
    wfz[z, True] = -1.0
    ab = [var_rep(q, [a]), var_rep(q, [b])]
    ba = [var_rep(q, [b]), var_rep(q, [a])]
    Z = WCNFMatrix(T, CNF([[z, -b], [-z, b]]), wfz, ab, ab)
    X = WCNFMatrix(T, CNF(), wfx, ab, ba)
    assert value(X * Z) == value(X) * value(Z)

def test_add():
    var_rep = get_var_rep_type()
    T = Index(3)
    q = T.q
    a, b = BoolVar(), BoolVar()
    ab = [var_rep(q, [a, b])]
    wf1 = WeightFunction([a, b])
    wf1.fill(1.0)
    cnf1 = CNF([[a, b], [-a, -b]])
    M1 = WCNFMatrix(T, cnf1, wf1, ab, ab)

    wf2 = WeightFunction([a, b])
    wf2.fill(1.0)
    wf2[a, True] = -2.0
    cnf2 = CNF()
    M2 = WCNFMatrix(T, cnf2, wf2, ab, ab)

    assert value(M1 + M2) == ConcreteMatrix(T, [
        [1.0, 0.0, 0.0],
        [0.0, 2.0, 0.0],
        [0.0, 0.0, -1.0],
    ])
