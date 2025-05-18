
# Installing and using the DPMC solver

Below are instructions for installing and using the DPMC solver. The installation requires Ubuntu. This has the following dependencies:

- make
- cmake 3.16
- automake 1.16
- g++ 11.2
- gmp 6.2
- boost (graph and system)
    - `sudo apt-get install libboost-all-dev`

These instructions use the LG tree decomposers with FlowCutter, and the DMC executor.

## Installation and setup

*The DPMC solver can be installed automatically by using `make solvers/DPMC`. If this does not work, try the description below.*

The solver can be downloaded into the current directory as follows:
```bash
git clone --recursive https://github.com/vardigroup/DPMC
cd DPMC
```
After this a planner and executor need to be built. First edit the `lg/src/util/graded_clauses.h` file to have an `#include <cstdint>` line at the top of the file. Build the LG planner using the following:
```bash
cd lg
make
```
For the LG planner to work, a solver needs to be build. While still in the `lg` folder, build the FlowCutter solver:
```bash
cd solvers/flow-cutter-pace17
make
```
Now edit the files:
- `addmc/libraries/cryptominisat/src/ccnr.cpp`
- `addmc/libraries/cryptominisat/src/ccnr.h`
to have `#include <cstdint>` at the top.

Now navigate back the the DPMC directory. Then build the DMC executor from its designated folder:
```bash
cd ../../../dmc
make dmc
```
After this all required dependencies are built. Navigate back to the DPMC folder to run the program on different `.cnf` files.

### Increasing precision of output

In the file `addmc/src/common.hh`, line 157 can be uncommented to remove the limit on precision of output.

## Usage

There are several examples of input files in the `examples` folder. We will use the `.cnf` files. The following commands convert the `.cnf` file to a tree decomposition using the LG planner, and then run the executor to get the weighted model count of the weighted CNF formula in the `.cnf` file:
```bash
cnfFile="./examples/50-10-1-q.cnf" && ./lg/build/lg "./lg/solvers/flow-cutter-pace17/flow_cutter_pace17 -p 100" <$cnfFile | ./dmc/dmc --cf=$cnfFile
```
Replace the filename in the first part of the command to the `.cnf` file you want to process.