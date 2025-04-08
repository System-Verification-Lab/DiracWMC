
from app.wcnf_matrix.cnf.cnf import CNF
from app.wcnf_matrix.cnf.boolvar import BoolVar
from app.wcnf_matrix.cnf.weights import WeightFunction

# x = BoolVar("x")
# y = BoolVar("y")
# wf = WeightFunction((x, y))
# wf.fill(1.0)
# wf[x, True] = 4.0
# cnf = CNF([[x, y]])
# cnf.subst(x, y)
# print(wf(cnf))

from app.wcnf_matrix.new_matrix import WCNFMatrix

print(WCNFMatrix.PauliZ)
print(WCNFMatrix.PauliZ._cnf)
print(WCNFMatrix.PauliZ._weight_func)
print(WCNFMatrix.PauliZ * WCNFMatrix.PauliZ)