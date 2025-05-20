
FROM python:3.13.3-bookworm

# Installation directory
WORKDIR /usr/src/app
# Dependencies for DPMC
RUN apt-get update
RUN apt-get install -y make cmake automake g++ g++-11 libgmp-dev \
libboost-all-dev

# Clone repository and fix bugs
RUN git clone --recursive https://github.com/vardigroup/DPMC
COPY ./add_include.py ./
RUN python add_include.py ./DPMC/lg/src/util/graded_clauses.h \
"#include <cstdint>"
RUN python add_include.py ./DPMC/addmc/libraries/cryptominisat/src/ccnr.cpp \
"#include <cstdint>"
RUN python add_include.py ./DPMC/addmc/libraries/cryptominisat/src/ccnr.h \
"#include <cstdint>"

# Run makefiles to install DPMC
RUN cd ./DPMC/lg && make
RUN cd ./DPMC/lg/solvers/flow-cutter-pace17 && make
RUN cd ./DPMC/dmc && make dmc

# Default run commands executes the solver using stdin and displays the result
COPY ./run_solver.py ./
CMD [ "python", "run_solver.py" ]
