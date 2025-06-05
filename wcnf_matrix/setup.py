
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
        client.containers.get("dpmc:latest")
        print("DPMC already installed!")
    except:
        client.images.build(path=docker_build_path, tag="dpmc")

def install_cachet():
    """ Install the Cachet solver using Docker """
    print("Installing cachet...")
    docker_build_path = os.path.join(os.path.dirname(__file__), "wcnf_matrix",
    "cnf", "model_counter", "solver", "cachet")
    client = docker.from_env()
    try:
        client.containers.get("cachet:latest")
        print("Cachet already installed!")
    except:
        try:
            client.images.build(path=docker_build_path, tag="cachet")
        except Exception as e:
            print(e)
            raise Exception()

install_dpmc()
install_cachet()
setuptools.setup()