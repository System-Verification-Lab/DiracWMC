from wcnf_matrix import *
from functools import reduce
I = Index(2)
r1, r2 = Reg(I), Reg(I)
phi = lambda index: reduce(lambda x, y: x + y, (ket(nv, nv) for nv in
uset(index)))
M = ket(I[0]) * bra(I[0])
print(value((M | r1) * (phi(I) | (r1, r2))))