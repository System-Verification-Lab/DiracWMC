
FROM python:3.8-slim

# Installation directory
WORKDIR /usr/src/app

# Update apt-get
RUN apt-get update
RUN apt-get upgrade -y

# Download TensorOrder source code
ADD https://github.com/vardigroup/TensorOrder/archive/6f59e6a2ffe37aa372e128d6c5ee089376a6d8c1.zip ./TensorOrder.zip
RUN apt-get install unzip
RUN unzip ./TensorOrder.zip
RUN rm -f ./TensorOrder.zip
RUN mv ./TensorOrder-6f59e6a2ffe37aa372e128d6c5ee089376a6d8c1 ./TensorOrder
WORKDIR /usr/src/app/TensorOrder

# Fix bugs in code
ADD ./fix_files.py ./fix_files.py
RUN python fix_files.py

# New METIS version that is still available
ADD https://github.com/KarypisLab/METIS/archive/refs/tags/v5.2.1.tar.gz /solvers/metis-5.2.1.tar.gz
ENV METIS_DLL=/solvers/metis-5.2.1/build/Linux-x86_64/libmetis/libmetis.so

# Added GKLib installation (dependency of new METIS)
ADD https://github.com/KarypisLab/GKlib/archive/refs/heads/master.zip /GKLib/GKLib.zip

RUN apt-get clean \
&& cd /var/lib/apt \
&& mv lists lists.old \
&& mkdir -p lists/partial \
&& apt-get update \
&& apt-get upgrade -y \
&& mkdir -p /usr/share/man/man1 \
# -------------------------
# Install OpenJDK 17 instead of 11
&& apt-get -y install g++ make libxml2-dev zlib1g-dev cmake openjdk-17-jdk libopenblas-dev \
# Dependecies of METIS and GKLib
&& apt-get -y install build-essential \
&& apt-get -y install cmake \
# Added GKLib installation (dependency of new METIS)
&& cd /GKLib/ \
&& apt-get install unzip \
&& unzip GKLib.zip \
&& rm GKLib.zip \
&& cd /GKLib/GKlib-master \
&& make config \
&& make \
&& make install \
# -------------------------
&& cd /solvers/ \
&& tar -xvf metis-5.2.1.tar.gz \
&& rm metis-5.2.1.tar.gz \
&& cd /solvers/METIS-5.2.1 \
&& make config shared=1 \
&& make \
&& make install \
&& pip install click numpy python-igraph networkx==2.1.0 metis turbine cython threadpoolctl jax jaxlib

RUN cd ./solvers/htd-master && cmake . && make
RUN cd ./solvers/TCS-Meiji && make heuristic
RUN cd ./solvers/flow-cutter-pace17 && make
RUN cd ./solvers/hicks && make
RUN cd ./solvers/portfolio && make
RUN cd ./src && make

ADD ./run_solver.py ./run_solver.py
CMD [ "python", "run_solver.py" ]