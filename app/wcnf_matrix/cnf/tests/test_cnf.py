
from ..cnf import CNF
from ..boolvar import BoolVar

def test_add():
    x, y, z, w = BoolVar(), BoolVar(), BoolVar(), BoolVar()
    a = CNF([[x, y]])
    b = CNF([[z], [w]])
    c = CNF([[x, y], [z], [w]])
    assert c == a + b

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

def inner_clause_order():
    a, b = BoolVar(), BoolVar()
    assert CNF([[a, b]]) == CNF([[b, a]])