
from wcnf_matrix import Index, Reg, ket, bra, uset, value
from functools import reduce

T = Index(2) # q-state potts, 2 = qubit
r1, r2 = Reg(T), Reg(T) # 2 different registers in Hilbert space
phi = lambda T: reduce(lambda x, y: x + y, (ket(nv, nv) for nv in uset(T))) # Python lambda expression
M = ket(T[0]) * bra(T[1])
print(value((M | r1) * (phi(T) | (r1, r2)))) # "value" evaluates all entries in the matrix