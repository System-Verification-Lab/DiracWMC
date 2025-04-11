
from app.wcnf_matrix import WCNFMatrix
from app.wcnf.solver import DPMCSolver
from app.quantum_ising import QuantumIsingModel

MODEL_FILE = "examples/quantum_ising/square.json"
BETA = 1.0

model = QuantumIsingModel.from_string(open(MODEL_FILE).read())
matrices: list[tuple[float, WCNFMatrix]] = []

for i, j, strength in model.interactions():
    zi = WCNFMatrix.PauliZ.local_matrix(1 << i, 1 << len(model))
    zj = WCNFMatrix.PauliZ.local_matrix(1 << j, 1 << len(model))
    matrices.append((BETA * strength, zi * zj))

for i in range(len(model)):
    zi = WCNFMatrix.PauliZ.local_matrix(1 << i, 1 << len(model))
    matrices.append((BETA * model.external_field_z, zi))
    xi = WCNFMatrix.PauliX.local_matrix(1 << i, 1 << len(model))
    matrices.append((BETA * model.external_field_x, xi))

hamiltonian = WCNFMatrix.linear_comb(*matrices)
trace_formula = hamiltonian.exp(15).trace()
solver = DPMCSolver()
print("True partition function:", model.partition_function(BETA))
print("Solver estimate:", solver.run_solver(trace_formula).total_weight)