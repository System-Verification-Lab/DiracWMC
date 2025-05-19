
import setuptools
from subprocess import check_call
import os

solver_dir = os.path.join(os.path.dirname(__file__), "wcnf_matrix", "solvers",
"DPMC")

def check_os():
    name = os.uname().sysname
    if name not in ("Linux", "Darwin"):
        raise Exception(f"Operating system \"{name}\" not supported")

def install_dpmc_requirements():
    """ Install packages required to run DPMC using apt """
    check_call(["sudo", "apt", "install", "-y", "make", "cmake", "automake",
    "g++", "libgmp-dev", "libboost-all-dev"], stdout=open("install.log", "w"))

def add_include_to_file(path: str, *line: str):
    """ Add an include directive to the given file. The directive is placed
        before the last include directive already present. Throws an error if
        there is no include directive present """
    content = open(path, "r").read()
    index = content.rfind("#include")
    content = content[:index] + "\n".join(line) + "\n" + content[index:]
    open(path, "w").write(content)

def install_dpmc():
    if os.path.exists(solver_dir):
        return
    os.makedirs(os.path.dirname(solver_dir), exist_ok=True)
    install_dpmc_requirements()
    check_call(["git", "clone", "--recursive",
    "https://github.com/vardigroup/DPMC"], cwd=os.path.dirname(solver_dir))
    add_include_to_file(os.path.join(solver_dir, "lg", "src", "util", "graded_clauses.h"), "#include <cstdint>")
    check_call(["make"], cwd=os.path.join(solver_dir, "lg"))
    check_call(["make"], cwd=os.path.join(solver_dir, "lg", "solvers",
    "flow-cutter-pace17"))
    add_include_to_file(os.path.join(solver_dir, "addmc", "libraries", "cryptominisat", "src", "ccnr.cpp"), "#include <cstdint>")
    add_include_to_file(os.path.join(solver_dir, "addmc", "libraries", "cryptominisat", "src", "ccnr.h"), "#include <cstdint>")
    check_call(["make", "dmc"], cwd=os.path.join(solver_dir, "dmc"))

check_os()
install_dpmc()

setuptools.setup()