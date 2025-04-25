
from wcnf_matrix import Index, uset
import pytest

def test_index():
    T1, T2 = Index(), Index()
    assert T1 != T2

def test_basis_eq():
    T = Index(field=complex)
    assert T[0] == T[0]

def test_basis_neq():
    T = Index(3)
    assert T[0] != T[1]

def test_different_space():
    T1, T2 = Index(), Index()
    assert T1[0] != T2[0]

def test_wrong_basis_elt():
    T = Index()
    with pytest.raises(ValueError):
        _ = T[4]

def test_basis_neq_other_type():
    T = Index()
    assert T[0] != 0

def test_uset():
    T = Index()
    for i, elt in zip(range(T.q), uset(T)):
        assert T[i] == elt