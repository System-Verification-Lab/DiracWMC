
from src.wcnf import WeightedCNF

formula = WeightedCNF.from_string(open("examples/cnf/simple.cnf").read())
print(formula.to_string())
print(formula.clauses)