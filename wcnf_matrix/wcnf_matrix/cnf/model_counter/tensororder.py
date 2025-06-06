
import docker
from docker.errors import NotFound, ContainerError
from typing import Iterator
from .model_counter import ModelCounter, ModelCounterResult
from ..cnf import CNF
from ..weights import WeightFunction
from .formats import format_cachet

class TensorOrder(ModelCounter):
    """ Interface to the TensorOrder model counter, which requires a docker
        image called "tensororder" to be present """

    def __init__(self):
        """ Constructor """
        self._client = docker.from_env()

    def model_count(self, cnf: CNF, weight_func: WeightFunction) -> (
    ModelCounterResult):
        """ Determine the value of weight_func(cnf) using the TensorOrder solver
            """
        weight_func = weight_func.copy()
        factor = weight_func.normalize()
        try:
            output = self._client.containers.run("tensororder:latest", command=[
            "python", "run_solver.py", format_cachet(cnf, weight_func)])
        except ContainerError:
            return ModelCounterResult(False)
        result = output.decode("utf-8")
        time_taken = count = None
        for line in result.split("\n"):
            if line.startswith("Total Time:"):
                time_taken = float(line.split()[-1])
            if line.startswith("Count:"):
                count = float(line.split()[-1])
        if count is None:
            return ModelCounterResult(False)
        if time_taken is None:
            time_taken = -1.0
        return ModelCounterResult(True, time_taken, count * factor)

    def batch_model_count(self, *problems: tuple[CNF, WeightFunction]) -> (
    Iterator[ModelCounterResult]):
        formats: list[str] = []
        factors: list[float] = []
        for cnf, weight_func in problems:
            weight_func = weight_func.copy()
            factors.append(weight_func.normalize())
            formats.append(format_cachet(cnf, weight_func))
        factors = list(reversed(factors))
        try:
            output = self._client.containers.run("tensororder:latest", command=[
            "python", "run_solver.py", *formats])
        except ContainerError:
            for _ in problems:
                yield ModelCounterResult(False)
            return
        result = output.decode("utf-8")
        if result == "ERR":
            for _ in problems:
                yield ModelCounterResult(False)
            return
        model_counts: list[float] = []
        runtimes: list[float] = []
        for line in result.split("\n"):
            if line.startswith("Total Time:"):
                runtimes.append(float(line.split()[-1]))
            if line.startswith("Count:"):
                model_counts.append(float(line.split()[-1]) * factors[-1])
                factors.pop()
        if len(model_counts) != len(problems):
            for _ in problems:
                yield ModelCounterResult(False)
            return
        for model_count, runtime in zip(model_counts, runtimes):
            yield ModelCounterResult(True, runtime, model_count)

    def is_available(self) -> bool:
        """ Returns if Cachet is available """
        try:
            self._client.images.get("tensororder:latest")
        except NotFound:
            return False
        return True