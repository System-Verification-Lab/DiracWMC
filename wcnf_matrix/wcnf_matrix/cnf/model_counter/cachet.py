
import docker
from docker.errors import NotFound
from typing import Iterator
from .model_counter import ModelCounter, ModelCounterResult
from ..cnf import CNF
from ..weights import WeightFunction
from .formats import format_cachet
import json
from subprocess import Popen, PIPE
from .config import RUNNER_VERSION

PROCESS_TIMEOUT = 30

class Cachet(ModelCounter):
    """ Interface to the Cachet model counter, which requires a docker image
        called "cachet" to be present """

    def __init__(self):
        """ Constructor """
        self._client = docker.from_env()

    def model_count(self, cnf: CNF, weight_func: WeightFunction) -> (
    ModelCounterResult):
        """ Determine the value of weight_func(cnf) using the Cachet solver """
        res = self.batch_model_count((cnf, weight_func))
        return next(res)

    def batch_model_count(self, *problems: tuple[CNF, WeightFunction]) -> (
    Iterator[ModelCounterResult]):
        problems, factors = self._normalize_problems(*problems)
        try:
            problem_strings = [format_cachet(cnf, wf) for cnf, wf in problems]
            problems_json = json.dumps({"problems": problem_strings})
            process = Popen(["docker", "run", "-i", "--rm",
            f"cachet:{RUNNER_VERSION}", "python", "run_solver.py"], stdin=PIPE,
            stdout=PIPE)
            output, _ = process.communicate(input=problems_json.encode(),
            timeout=PROCESS_TIMEOUT)
        except:
            for _ in problems:
                yield ModelCounterResult(False)
        results = json.loads(output.decode())
        for result, factor in zip(results["results"], factors):
            model_count = None
            runtime = -1.0
            for line in result.split("\n"):
                if line.startswith("Satisfying probability"):
                    model_count = float(line.split()[-1]) * factor
                if line.startswith("RUNTIME:"):
                    runtime = float(line.split()[-1])
            yield ModelCounterResult(model_count is not None, runtime,
            model_count)

    def is_available(self) -> bool:
        """ Returns if Cachet is available """
        try:
            self._client.images.get("cachet:latest")
        except NotFound:
            return False
        return True
    
    def _normalize_problems(self, *problems: tuple[CNF, WeightFunction]) -> (
    tuple[list[tuple[CNF, WeightFunction]], list[float]]):
        """ Normalize the weight functions of the given problems, and return a
            list of the new problems and a list of factors, with which the model
            counts of the new problems need to be multiplied to get the model
            counts of the original problems """
        new_problems = []
        factors = []
        for cnf, wf in problems:
            wf = wf.copy()
            factors.append(wf.normalize())
            new_problems.append((cnf, wf))
        return new_problems, factors