
from app.models import QuantumIsingModel
from app.converters import quantum_ising_to_ising, quantum_ising_to_wcnf
from app.cmdargs import Arguments
from app.logger import log_info, log_stat

args = Arguments()

log_info("Reading input file...")
with open(args.filename, "r") as input_file:
    quantum_model = QuantumIsingModel.from_string(input_file.read())

log_info("Converting to wCNF fomrula...")
wcnf = quantum_ising_to_wcnf(quantum_model, args.beta, args.layers)

log_info("Converting to Classical Ising Model...")
model, factor = quantum_ising_to_ising(quantum_model, args.beta, args.layers)
log_stat("QI->I Multiplication factor", factor)

if args.solver is None:
    # Normalize weights for Cachet formatted files
    if args.output_format == "cachet":
        log_info("Normalizing wCNF weights...")
        normalize_factor = wcnf.weights.normalize()
        log_stat("wCNF normalization factor", normalize_factor)
    log_info(f"Writing to output file {args.output_filename}...")
    with open(args.output_filename, "w") as output_file:
        output_file.write(wcnf.to_string(args.output_format))
else:
    result = args.solver.run_solver(wcnf)
    if not result.success:
        raise RuntimeError("Something went wrong while running the solver")
    quantum_partition_est = result.total_weight
    log_stat(f"Quantum partition function (est.)",
    quantum_partition_est)

# Debug mode >= 1: Calculate quantum partition function manually
if args.debug_level >= 1:
    log_info("Calculating quantum partition function...")
    quantum_partition = quantum_model.partition_function(args.beta)
    log_stat(f"Quantum partition function (exact)", quantum_partition)
# Debug mode >= 2: Calculate all values manually
if args.debug_level >= 2:
    log_info("Calculating classical partition function...")
    classical_partition = model.partition_function(1.0)
    log_stat("Classical partition function", classical_partition)
    log_info("Calculating wCNF weight using brute-force...")
    wcnf_weight = wcnf.total_weight()
    log_stat("Weight of wCNF formula", wcnf_weight)