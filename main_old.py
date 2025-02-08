
from src.models import QuantumIsingModel
from src.converters import ising_to_wcnf, quantum_ising_to_ising
from src.cmdargs import Arguments
from src.logger import log_info, log_stat
from src.wcnf import format_wcnf
from pathlib import Path

args = Arguments()

log_info("Reading input file...")
with open(args.filename, "r") as input_file:
    quantum_model = QuantumIsingModel.from_string(input_file.read())

log_info("Converting to Classical Ising Model...")
model, factor = quantum_ising_to_ising(quantum_model, args.beta, args.layers)
log_stat("QI->I Multiplication factor", factor)

if args.create_ising:
    ising_filename = str(Path(args.output_filename).with_suffix(".json"))
    log_info(f"Writing to output file {ising_filename}...")
    with open(ising_filename, "w") as ising_file:
        ising_file.write(str(model))

log_info("Converting to wCNF formula...")
wcnf = ising_to_wcnf(model, 1.0)
log_info("Adding missing weights...")
wcnf.add_missing_weights()
# Normalize weights for Cachet formatted inputs
normalize_factor = 1.0
if args.output_format == "cachet":
    log_info("Normalizing wCNF weights...")
    normalize_factor = wcnf.normalize_weights()
    log_stat("wCNF normalization factor", normalize_factor)

if args.solver is None:
    log_info(f"Writing to output file {args.output_filename}...")
    with open(args.output_filename, "w") as output_file:
        output_file.write(format_wcnf(wcnf, args.output_format))
else:
    solver_output = args.solver.calculate_weight(wcnf)
    quantum_partition_est = solver_output * factor * normalize_factor
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