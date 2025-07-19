# Quantum Ising Model approximation using wCNF formulae

This folder contains tools that can approximate quantum Ising model partition functions using weighted CNF formulae. The quantum Ising models should be given as JSON files (see the [examples folder](./examples/)).

## Input format

The Quantum Ising Model should be represented using a JSON file with a root object with up to four children:
- `spin_count` is an integer with the number of nodes/spins in the system
- `external_field_x` is the external field strength in the x-direction as a float
- `external_field_z` is the external field strength in the z-direction as a float
- `interaction` is a list of interactions. An interaction is represented using a list of three items: First the two nodes that are connected (as integers) and then the strength of the interaction (as a float). An example of a system with two nodes with transverse field strength 1 and an interaction of strength 1 is shown below:
```json
{
    "spin_count": 2,
    "external_field_x": 1, // Optional, defaults to 0
    "external_field_z": 0, // Optional, defaults to 0
    "interaction": [
        [0, 1, 1]
    ]
}
```

## Installing a solver

To approximate the partition function of a model using a weighted CNF formula, model counters need to be installed. These are four supported model counters: Cachet, DPMC, Ganak, and TensorOrder. IThe folder `docs/solvers` contains instructions on how to install the different solvers. Please note that solvers should be installed in a folder `solvers/[solver-name]` to work properly with this application.

## List of tools

Run the following command to get an overview of all of the different tools, such as converting a quantum Ising model to a weighted CNF file, and calling a solver:
```sh
python -m app
```
Note that all tools should be run with the command prefix `python -m`, as described when running the above command.