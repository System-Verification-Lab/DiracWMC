from wcnf_matrix import *
from functools import reduce
I = Index(2)
M1 = 2 * ket(I[0]) * bra(I[0]) + ket(I[1]) * bra(I[1])
M2 = reduce(lambda x, y: x ** y, [M1]*100)
cnf, weight_func = M2.trace_formula()
print(weight_func(cnf))

# Added to example 4:
B = reduce(lambda x, y: x ** y, [bra(I[0])]*100)
K = reduce(lambda x, y: x ** y, [ket(I[0])]*100)
print(value(B * M2 * K))