
import docker
import os
import setuptools

def install_dpmc():
    """ Install the DPMC solver using Docker """
    print("Installing DPMC...")
    docker_build_path = os.path.join(os.path.dirname(__file__), "wcnf_matrix",
    "cnf", "model_counter", "solver", "DPMC")
    client = docker.from_env()
    try:
        client.images.get("dpmc:latest")
        print("DPMC already installed!")
    except:
        client.images.build(path=docker_build_path, tag="dpmc")

def install_cachet():
    """ Install the Cachet solver using Docker """
    print("Installing Cachet...")
    docker_build_path = os.path.join(os.path.dirname(__file__), "wcnf_matrix",
    "cnf", "model_counter", "solver", "cachet")
    client = docker.from_env()
    try:
        client.images.get("cachet:latest")
        print("Cachet already installed!")
    except:
        client.images.build(path=docker_build_path, tag="cachet")

def install_tensororder():
    """ Install the TensorOrder solver using Docker """
    print("Installing TensorOrder...")
    docker_build_path = os.path.join(os.path.dirname(__file__), "wcnf_matrix",
    "cnf", "model_counter", "solver", "TensorOrder")
    client = docker.from_env()
    try:
        client.images.get("tensororder:latest")
        print("TensorOrder already installed!")
    except:
        client.images.build(path=docker_build_path, tag="tensororder")

install_dpmc()
install_cachet()
install_tensororder()
setuptools.setup()