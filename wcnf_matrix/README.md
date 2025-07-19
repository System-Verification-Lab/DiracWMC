
# WCNF Matrix

A tool for matrix representation using logical formulae and weight functions.

## Requirements

The package requires Python 3.12 or higher and docker to be installed on the system. It has been tested in WSL, but should work across operating systems.

## Installation

The python package can be installed by navigating to the folder this README is contained in, and running
```sh
python -m pip install .
```
Optionally you may want to install the package in a virtual environment.

> [!IMPORTANT]
> The installation will take a long time to finish, and may seem to freeze. This is due to the DPMC, Cachet, and TensorOrder model counters being installed alongside the package. The package still functions correctly when only installing DPMC. If you would like to only install DPMC, remove the lines `install_cachet() and `install_tensororder()` from [setup.py](./setup.py)

## Usage

The package can be imported from python by the name `wcnf_matrix`. The following functions/classes are included:

| Name/Signature | Description |
| --- | --- |
| `Index(q)` | Creates a q-state Hilbert space |
| `uset(T)` | Iterator over all basis elements of index `T` |
| `Reg(T)` | Create a register in the Hilbert space of index `T` |
| `bra(b0, ..., bn)` | Create a row vector from basis elements of the same index |
| `ket(b0, ..., bn)` | Create a column vector from basis elements of the same index |
| `value(m)` | Evaluate all entries of the matrix using DPMC. Returns a `ConcreteMatrix` object |

In general, you want to create an `Index` first, which represents a separate "space" on which operations are performed. Here the number of states can be passed. Then operations can be performed by using `bra(T[i])` and `ket(T[i])`, which create a bra/ket vector from the `i`'th basis element of `T`.

The `value` function can be called with as a parameter a matrix, such that all of the entries in the matrix will be evaluated using DPMC. Optionally matrices can be labeled with register names (see the example below).

Operators that work on matrices are `*` (scalar and matrix multiplication), `+` (addition), `-` (subtraction), and `**` (kronecker product of matrices).

## Example

```py
from wcnf_matrix import *
from functools import reduce

T = Index(2) # q-state potts, 2 = qubit
r1, r2 = Reg(T), Reg(T) # 2 different registers in Hilbert space
phi = lambda T: reduce(lambda x, y: x + y, (ket(nv, nv) for nv in uset(T))) # Python lambda expression
M = ket(T[0]) * bra(T[0])
print(value((M | r1) * (phi(T) | (r1, r2)))) # "value" evaluates all entries in the matrix
```