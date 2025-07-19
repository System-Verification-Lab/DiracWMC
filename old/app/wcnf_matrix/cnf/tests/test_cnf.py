
from ..cnf import CNF
from ..boolvar import BoolVar

def test_add():
    x, y, z, w = BoolVar(), BoolVar(), BoolVar(), BoolVar()
    a = CNF([[x, y]])
    b = CNF([[z], [w]])
    c = CNF([[x, y], [z], [w]])
    assert c == a + b
    assert c == a & b

def test_not_add():
    x, y, z = BoolVar(), BoolVar(), BoolVar()
    a = CNF([[x, y]])
    b = CNF([[z]])
    c = CNF([[x], [y], [z]])
    assert a + b != c

def test_add_clause():
    x, y, z = BoolVar(), BoolVar(), BoolVar()
    a = CNF([[x, y], [x]])
    a.add_clause([x, z])
    assert a == CNF([[x, y], [x], [x, z]])

def test_inner_clause_order():
    a, b = BoolVar(), BoolVar()
    assert CNF([[a, b]]) == CNF([[b, a]])

def test_subst():
    a, b = BoolVar(), BoolVar()
    cnf = CNF([[a]])
    cnf.subst(a, b)
    assert cnf == CNF([[b]])

def test_bulk_subst():
    a, b, c, d = BoolVar(), BoolVar(), BoolVar(), BoolVar()
    cnf = CNF([[a, b], [c]])
    cnf.bulk_subst({a: b, b: c, c: a})
    assert cnf == CNF([[c, b], [a]])