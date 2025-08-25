from wcnf_matrix import *
I = Index(3)
M1 = ket(I[0]) * bra(I[1])
M2 = ket(I[2]) * bra(I[0])
print(value(M1 * M2))
print(value(3.3 * M1 + M2))
print(value(M1 ** M2))