
# 1. Updated Dockerfile
```Dockerfile
FROM python:3.8-slim

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

COPY solvers/htd-master /solvers/htd-master
RUN cd /solvers/htd-master \
&& cmake . \
&& make

COPY solvers/TCS-Meiji /solvers/TCS-Meiji
RUN cd /solvers/TCS-Meiji \
&& make heuristic

COPY solvers/flow-cutter-pace17 /solvers/flow-cutter-pace17
RUN cd /solvers/flow-cutter-pace17 \
&& make

COPY solvers/hicks /solvers/hicks
RUN cd /solvers/hicks \
&& make

COPY solvers/portfolio /solvers/portfolio
RUN cd /solvers/portfolio \
&& make

COPY src /src
RUN cd /src \
&& make
```

# 2. Fix compiler & deprecation errors

- In file `solvers/flow-cutter-pace17/src/list_graph.h` after line 6 add `#include <string>`
- In file `src/tensor_network/tensor_apis/numpy_apis.py` line 21, replace `self._numpy.object` with `object`
- In file `src/tensororder.py` line 214, replace `is not` with `!=`