
Updated Dockerfile:
```Dockerfile
FROM python:3.7-slim

# New METIS version that is still available
ADD https://github.com/KarypisLab/METIS/archive/refs/tags/v5.2.1.tar.gz /solvers/metis-5.2.1.tar.gz
ENV METIS_DLL=/solvers/metis-5.2.1/build/Linux-x86_64/libmetis/libmetis.so

# Added GKLib installation (dependency of new METIS)
ADD https://github.com/KarypisLab/GKlib/archive/refs/tags/METIS-v5.1.1-DistDGL-0.5.tar.gz /GKLib/GKLib.tar.gz

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
&& tar -xvf GKLib.tar.gz \
&& rm GKLib.tar.gz \
&& cd /GKLib/GKlib-METIS-v5.1.1-DistDGL-0.5 \
&& make config openmp=set \
&& make \
&& make install \
# -------------------------
&& cd /solvers/ \
&& tar -xvf metis-5.2.1.tar.gz \
&& rm metis-5.2.1.tar.gz \
&& cd /solvers/METIS-5.2.1 \
&& make config shared=1 gklib_path=~/local \
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