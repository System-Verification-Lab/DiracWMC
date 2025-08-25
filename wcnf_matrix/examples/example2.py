from wcnf_matrix import *
I = Index(3)
M = ket(I[0]) * bra(I[1])
M1 = Index(2)
print(value(M))
