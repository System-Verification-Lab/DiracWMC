
import docker
from docker.errors import NotFound
from typing import Iterator
from time import time
from .model_counter import ModelCounter, ModelCounterResult
from ..cnf import CNF
from ..weights import WeightFunction
from .formats import format_dpmc

class DPMC(ModelCounter):
    """ Interface to the DPMC model counter, which needs to be installed under
        the solvers/DPMC folder in the current working directory """

    def __init__(self):
        """ Constructor """
        self._client = docker.from_env()

    def model_count(self, cnf: CNF, weight_func: WeightFunction) -> (
    ModelCounterResult):
        """ Determine the value of weight_func(cnf) using the DPMC solver """
        start = time()
        output = self._client.containers.run("dpmc:latest", command=["python",
        "run_solver.py", format_dpmc(cnf, weight_func)])
        end = time()
        result = output.decode("utf-8")
        for line in result.split("\n"):
            if line.startswith("c s exact double prec-sci"):
                weight = float(line.split()[-1])
                return ModelCounterResult(True, end - start, weight)
        return ModelCounterResult(False)

    def batch_model_count(self, *problems: tuple[CNF, WeightFunction]) -> (
    Iterator[ModelCounterResult]):
        output = self._client.containers.run("dpmc:latest", command=["python",
        "run_solver.py", *(format_dpmc(cnf, weight_func) for cnf, weight_func in
        problems)])
        result = output.decode("utf-8")
        if result == "ERR":
            for _ in problems:
                yield ModelCounterResult(False)
            return
        model_counts: list[float] = []
        runtimes: list[float] = []
        for line in result.split("\n"):
            if line.startswith("c s exact double prec-sci"):
                model_counts.append(float(line.split()[-1]))
            if line.startswith("c seconds"):
                runtimes.append(float(line.split()[-1]))
        for model_count, runtime in zip(model_counts, runtimes):
            yield ModelCounterResult(True, runtime, model_count)

    def is_available(self) -> bool:
        """ Returns if DPMC is available """
        try:
            self._client.containers.get("dpmc:latest")
        except NotFound:
            return False
        return True