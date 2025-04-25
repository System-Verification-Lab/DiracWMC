
from wcnf_matrix import Index, Matrix, bra, ket

def test_bra_ket_mul():
    T = Index()
    assert Matrix(T, [[0, 1], [0, 0]]) == ket(T[0]) * bra(T[1])

def test_neq_different_index():
    T1, T2 = Index(), Index()
    assert Matrix(T1, [[3]]) != Matrix(T2, [[3]])

def test_eq_small():
    T = Index()
    assert Matrix(T, [[4]]) == Matrix(T, [[4]])