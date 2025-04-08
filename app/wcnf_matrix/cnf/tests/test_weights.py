
from pytest import approx
from ..boolvar import BoolVar
from ..weights import WeightFunction

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
    x, y, z = BoolVar(), BoolVar(), BoolVar()
    f = WeightFunction([x, y])
    f[x, True] = 98.0
    f[z, False] = -1.5
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
    f.combine(g, lambda a, b: a * b)
    assert f[y, True] == approx(10.0)
