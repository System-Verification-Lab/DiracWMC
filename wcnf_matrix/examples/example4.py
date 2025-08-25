from wcnf_matrix import *
from functools import reduce
I = Index(2)
M1 = 2 * ket(I[0]) * bra(I[0]) + ket(I[1]) * bra(I[1])
M2 = reduce(lambda x, y: x ** y, [M1]*100)
cnf, weight_func = M2.trace_formula()
print(weight_func(cnf))