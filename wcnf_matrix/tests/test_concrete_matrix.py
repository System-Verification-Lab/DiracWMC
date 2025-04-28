
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

def test_permutation():
    T = Index()
    X = ConcreteMatrix(T, [[0, 1], [1, 0]])
    Z = ConcreteMatrix(T, [[1, 0], [0, -1]])
    assert X ** Z == (Z ** X).permutation([1, 0])

def test_permutation_2():
    T = Index()
    A = ConcreteMatrix(T, [[1, 2], [3, 4]])
    B = ConcreteMatrix(T, [[5, 6], [7, 8]])
    assert A ** B == (B ** A).permutation([1, 0])

def test_permutation_3():
    T = Index()
    M = ConcreteMatrix(T, [[1, 4], [5, 2]])
    assert M == M.permutation([0])

def test_permutation_4():
    T = Index()
    M = ConcreteMatrix(T, [[1], [5], [4], [3]])
    assert M.permutation([], [1, 0]) == ConcreteMatrix(T, [[1], [4], [5], [3]])