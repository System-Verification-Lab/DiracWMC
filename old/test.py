
from app.wcnf_matrix import WCNFMatrix, pack_wcnf_formula
from app.wcnf.solver import DPMCSolver
from app.quantum_ising import QuantumIsingModel

MODEL_FILE = "examples/quantum_ising/two_spin.json"
BETA = 1.0

model = QuantumIsingModel.from_string(open(MODEL_FILE).read())
matrices: list[tuple[float, WCNFMatrix]] = []

for i, j, strength in model.interactions():
    zi = WCNFMatrix.PauliZ.local_matrix(i, len(model))
    zj = WCNFMatrix.PauliZ.local_matrix(j, len(model))
    matrices.append((BETA * strength, zi * zj))

for i in range(len(model)):
    zi = WCNFMatrix.PauliZ.local_matrix(i, len(model))
    matrices.append((BETA * model.external_field_z, zi))
    xi = WCNFMatrix.PauliX.local_matrix(i, len(model))
    matrices.append((BETA * model.external_field_x, xi))

hamiltonian = WCNFMatrix.linear_comb(*matrices)
cnf, weight_func = hamiltonian.exp(15).trace()
trace_formula = pack_wcnf_formula(cnf, weight_func)
solver = DPMCSolver()
print("True partition function:", model.partition_function(BETA))
print("Solver estimate:", solver.run_solver(trace_formula).total_weight)