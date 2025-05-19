
import os
from subprocess import Popen, PIPE, TimeoutExpired
from tempfile import NamedTemporaryFile
from time import time
from .model_counter import ModelCounter, ModelCounterResult
from ..cnf import CNF
from ..weights import WeightFunction
from .formats import format_dpmc

src_folder = os.path.join(os.path.dirname(__file__), "..", "..", "solvers", "DPMC")

class DPMC(ModelCounter):
    """ Interface to the DPMC model counter, which needs to be installed under
        the solvers/DPMC folder in the current working directory """

    def model_count(self, cnf: CNF, weight_func: WeightFunction) -> (
    ModelCounterResult):
        if not self.is_available():
            raise RuntimeError("DPMC solver not available")
        temp_file = self._create_file(cnf, weight_func)
        infile = open(temp_file.name, "r")
        p1 = Popen(["./lg/build/lg", "./lg/solvers/flow-cutter-pace17/"
        "flow_cutter_pace17 -p 100"], cwd=src_folder, stdout=PIPE, stdin=
        infile)
        p2 = Popen(["./dmc/dmc", f"--cf={temp_file.name}"], cwd=src_folder,
        stdout=PIPE, stdin=p1.stdout)
        start = time()
        try:
            output, _ = p2.communicate(timeout=self._timeout)
        except TimeoutExpired:
            return ModelCounterResult(False)
        end = time()
        result = output.decode("utf-8")
        for line in result.split("\n"):
            if line.startswith("c s exact double prec-sci"):
                weight = float(line.split()[-1])
                return ModelCounterResult(True, end - start, weight)
        return ModelCounterResult(False)

    def is_available(self) -> bool:
        return os.path.isdir(src_folder)
    
    def _create_file(self, cnf: CNF, weight_func: WeightFunction):
        """ Create a temporary file with the formatted version of the weighted
            CNF formula and return the temporary file reference """
        temp_file = NamedTemporaryFile()
        with open(temp_file.name, "w") as f:
            f.write(format_dpmc(cnf, weight_func))
        return temp_file