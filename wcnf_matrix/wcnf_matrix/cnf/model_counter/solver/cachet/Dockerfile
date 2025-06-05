
FROM python:3.13.3-bookworm

# Installation directory
WORKDIR /usr/src/app
# Dependencies for Cachet
RUN apt-get update
RUN apt-get install -y g++ make linux-headers-generic

# Download cachet
ADD https://www.cs.virginia.edu/~rmw7my/Cachet/cachet-wmc-1-21.zip ./cachet.zip
RUN unzip cachet.zip
RUN rm cachet.zip
RUN mv cachet-wmc-* cachet
# Run script that fixes some missing includes and the makefile
COPY ./fix_missing.py ./
RUN python fix_missing.py
RUN ln -s /usr/src/linux-headers-*-common/include/linux/sys.h /usr/include/linux/sys.h
# Build Cachet
RUN cd ./cachet && rm -f *.o
RUN cd ./cachet && make

# Default run command executes solver using stdin or passed command line args
COPY ./run_solver.py ./
CMD [ "python", "run_solver.py" ]
