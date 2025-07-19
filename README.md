# Quantum Computation using Weighted Model Counting

This is the code for the thesis "Quantum Computation using Weighted Model Counting". The folder `wcnf_matrix` contains a Python package for performing matrix operations using WMC representations. See the [README](./wcnf_matrix/README.md) in this folder for installation and usage instructions.

## Experiments

When the `wcnf_matrix` package is installed, several experiments from the thesis can run. These are contained in the folder [experiments](./experiments). The following commands can be run
```sh
python -m experiments.ising # Classical Ising model
python -m experiments.potts # Classical Potts model
python -m experiments.quantum_ising # Transverse-field Ising model
```