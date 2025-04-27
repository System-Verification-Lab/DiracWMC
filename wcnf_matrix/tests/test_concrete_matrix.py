
from wcnf_matrix import Index, ConcreteMatrix, bra, ket

def test_bra_ket_mul():
    T = Index()
    assert ConcreteMatrix(T, [[0, 1], [0, 0]]) == ket(T[0]) * bra(T[1])

def test_neq_different_index():
    T1, T2 = Index(), Index()
    assert ConcreteMatrix(T1, [[3]]) != ConcreteMatrix(T2, [[3]])

def test_eq_small():
    T = Index()
    assert ConcreteMatrix(T, [[4]]) == ConcreteMatrix(T, [[4]])

def test_kron():
    T = Index()
    assert ConcreteMatrix(T, [
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 1, 0, 0],
        [0, 1, 0, 0],
    ]) == ConcreteMatrix(T, [[0, 1], [1, 0]]) ** ConcreteMatrix(T, [[0, 1], [0, 1]])