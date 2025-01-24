# Quantum Ising Model approximation using wCNF formulas

This folder contains a program that can convert Quantum Ising Models in a specific JSON format to wCNF formulas. This can then be used to estimate the partition function of the quantum model.

## Input format

The Quantum Ising Model should be represented using a JSON file with a root object with three children: `nodes` is an integer with the number of nodes in the system, `external_factor` is the external field strength as a float, `interactions` is a list of interactions. An interaction is represented using a list of three items: First the two nodes that are connected (as integers) and then the strength of the interaction (as a float). An example of a system with two nodes with external field strength 1 and an interaction of strength 1 is shown below:
```json
{
    "nodes": 2,
    "external_factor": 1,
    "interactions": [
        [0, 1, 1]
    ]
}
```

## Installing a solver

Different solvers have different installation requirements. The folder `docs/solvers` contains instructions on how to install the different solvers. Please note that solvers should be installed in a folder `solvers/[solver-name]` to work properly with this application.

## Running the conversion tool

To create an approximation wCNF formula and run the solver on it to get an approximation of the parition function, run the following:
```sh
python main.py filename
```
Here the filename is a JSON file with the correct input format. This generates an `output.cnf` file with the wCNF formula specification. The quantum partition function approximation is shown in the terminal. For more options, use
```sh
python main.py -h
```