
from pytest import approx
from wcnf_matrix import BoolVar, WeightFunction

def test_combine_domains():
    x, y = BoolVar(), BoolVar()
    f = WeightFunction([x])
    g = WeightFunction([y])
    assert f.combine(g, lambda a, b: a * b).domain == set([x, y])

def test_subst_domain():
    x, y = BoolVar(), BoolVar()
    f = WeightFunction([x])
    f.subst(x, y)
    assert f.domain == set([y])
    assert f == WeightFunction([y])

def test_bulk_subst_domain():
    x, y, z = BoolVar(), BoolVar(), BoolVar()
    f = WeightFunction([x, y])
    f.bulk_subst({x: y, y: z})
    assert f.domain == set([y, z])

def test_bulk_subst_values():
    x, y, z = BoolVar("x"), BoolVar("y"), BoolVar("z")
    f = WeightFunction([x, y])
    f[x, True] = 98.0
    f[y, False] = -1.5
    f.bulk_subst({x: y, y: z})
    assert f[y, True] == 98.0
    assert f[z, False] == -1.5

def test_bulk_subst_and_combine():
    x, y, z = BoolVar(), BoolVar(), BoolVar()
    f = WeightFunction([x, y])
    f[y, True] = 5.0
    g = WeightFunction([z])
    g[z, True] = 2.0
    g.bulk_subst({z: y})
    h = f.combine(g, lambda a, b: a * b)
    assert h[y, True] == approx(10.0)
