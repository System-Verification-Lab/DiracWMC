
import docker
import os
import setuptools

# Path to the folder with the DPMC Dockerfile and scripts
docker_build_path = os.path.join(os.path.dirname(__file__), "wcnf_matrix",
"cnf", "model_counter", "solver", "DPMC")

# Create DPMC docker image
client = docker.from_env()
try:
    client.containers.get("dpmc:latest")
except:
    client.images.build(path=docker_build_path, tag="dpmc")

setuptools.setup()