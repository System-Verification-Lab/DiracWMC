
import docker
from docker.errors import ImageNotFound
from typing import Iterator
from .model_counter import ModelCounter, ModelCounterResult
from ..cnf import CNF
from ..weights import WeightFunction
from .formats import format_dpmc
from subprocess import Popen, PIPE
import json
from .config import RUNNER_VERSION

PROCESS_TIMEOUT = 30

class DPMC(ModelCounter):
    """ Interface to the DPMC model counter, which requires a docker image
        called "dpmc" to be present """

    def __init__(self):
        """ Constructor """
        self._client = docker.from_env()

    def model_count(self, cnf: CNF, weight_func: WeightFunction) -> (
    ModelCounterResult):
        """ Determine the value of weight_func(cnf) using the DPMC solver """
        res = self.batch_model_count((cnf, weight_func))
        return next(res)

    def batch_model_count(self, *problems: tuple[CNF, WeightFunction]) -> (
    Iterator[ModelCounterResult]):
        try:
            problem_strings = [format_dpmc(cnf, wf) for cnf, wf in problems]
            problems_json = json.dumps({"problems": problem_strings})
            process = Popen(["docker", "run", "-i", "--rm",
            f"dpmc:{RUNNER_VERSION}", "python", "run_solver.py"], stdin=PIPE,
            stdout=PIPE)
            output, _ = process.communicate(input=problems_json.encode(),
            timeout=PROCESS_TIMEOUT)
        except:
            for _ in problems:
                yield ModelCounterResult(False)
        results = json.loads(output.decode())
        for result in results["results"]:
            model_count = None
            runtime = -1.0
            for line in result.split("\n"):
                if line.startswith("c s exact double prec-sci"):
                    model_count = float(line.split()[-1])
                if line.startswith("c seconds"):
                    runtime = float(line.split()[-1])
            yield ModelCounterResult(model_count is not None, runtime,
            model_count)

    def is_available(self) -> bool:
        """ Returns if DPMC is available """
        try:
            self._client.images.get("dpmc:latest")
        except ImageNotFound:
            return False
        return True