
import docker
import os
import setuptools

RUNNER_VERSION = "1.7"

def install_dpmc():
    """ Install the DPMC solver using Docker """
    print("Installing DPMC...")
    docker_build_path = os.path.join(os.path.dirname(__file__), "wcnf_matrix",
    "cnf", "model_counter", "solver", "DPMC")
    client = docker.from_env()
    tag = f"dpmc:{RUNNER_VERSION}"
    try:
        client.images.get(tag)
        print("DPMC already installed!")
    except:
        client.images.build(path=docker_build_path, tag=tag)

def install_cachet():
    """ Install the Cachet solver using Docker """
    print("Installing Cachet...")
    docker_build_path = os.path.join(os.path.dirname(__file__), "wcnf_matrix",
    "cnf", "model_counter", "solver", "cachet")
    client = docker.from_env()
    tag = f"cachet{RUNNER_VERSION}"
    try:
        client.images.get(f"{tag}:latest")
        print("Cachet already installed!")
    except:
        client.images.build(path=docker_build_path, tag=tag)

def install_tensororder():
    """ Install the TensorOrder solver using Docker """
    print("Installing TensorOrder...")
    docker_build_path = os.path.join(os.path.dirname(__file__), "wcnf_matrix",
    "cnf", "model_counter", "solver", "TensorOrder")
    client = docker.from_env()
    tag = f"tensororder{RUNNER_VERSION}"
    try:
        client.images.get(f"{tag}:latest")
        print("TensorOrder already installed!")
    except:
        client.images.build(path=docker_build_path, tag=tag)

install_dpmc()
# install_cachet()
# install_tensororder()
setuptools.setup()