
from .wcnf import WeightedCNF
from .formats import format_wcnf
from ..logger import log_info, log_stat
import os
from subprocess import Popen, PIPE
from time import time

class SolverInterface:
    """ Generic solver interface """

    def __init__(self, output_path: str = "output.cnf"):
        """ Constructor. An output file path can be given to output produced
            .cnf file to """
        self._output_path = output_path

    def calculate_from_file(self, filename: str) -> float:
        """ Calculate total weight of wCNF formula in the given .cnf file """
        raise NotImplementedError

    def format_formula(self, formula: WeightedCNF) -> str:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        raise NotImplementedError

    def calculate_weight(self, formula: WeightedCNF) -> float:
        """ Output the given formula to the specified output file and calculate
            the total weight using the solver. Returns the total weight """
        log_info("Creating output file...")
        self.make_output_file(formula)
        log_info("Running solver...")
        start = time()
        result = self.calculate_from_file(self._output_path)
        end = time()
        log_stat("Solver output", str(result))
        log_stat("Runtime", f"{end - start:.3f} s")
        return result

    def make_output_file(self, formula: WeightedCNF):
        """ Create output .cnf file with correctly formatted content """
        with open(self._output_path, "w") as f:
            f.write(self.format_formula(formula))

class DPMCSolverInterface(SolverInterface):
    """ Solver interface for the DPMC solver """

    def calculate_from_file(self, filename: str) -> float:
        """ Calculate total weight of wCNF formula in the given .cnf file """
        cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..",
        "..", "solvers", "DPMC")
        filepath = os.path.join(os.getcwd(), filename)
        infile = open(filepath, "r")
        p1 = Popen(["./lg/build/lg", "./lg/solvers/flow-cutter-pace17/"
        "flow_cutter_pace17 -p 100"], cwd=cwd, stdout=PIPE, stdin=infile)
        p2 = Popen(["./dmc/dmc", f"--cf={filepath}"], cwd=cwd, stdout=PIPE,
        stdin=p1.stdout)
        result = p2.stdout.read().decode("utf-8")
        for line in result.split("\n"):
            if line.startswith("c s exact double prec-sci"):
                return float(line.split()[-1])
        raise Exception("Could not find result of DPMC. Something must have "
        "gone wrong while running it")
    
    def format_formula(self, formula: WeightedCNF) -> str:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        return format_wcnf(formula, "dpmc")

class CachetSolverInterface(SolverInterface):
    """ Solver interface for the Cachet solver """

    def calculate_from_file(self, filename: str) -> float:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..",
        "..", "solvers", "cachet")
        filepath = os.path.join(os.getcwd(), filename)
        p = Popen(["./cachet", filepath], cwd=cwd, stdout=PIPE)
        result = p.stdout.read().decode("utf-8")
        for line in result.split("\n"):
            if line.startswith("Satisfying probability"):
                return float(line.split()[-1])
        raise Exception("Could not find result of Cachet. Something must have "
        "gone wrong while running it")
    
    def format_formula(self, formula: WeightedCNF) -> str:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        return format_wcnf(formula, "cachet")
    
class TensorOrderSolverInterface(SolverInterface):
    """ Solver interface for the TensorOrder solver """

    def calculate_from_file(self, filename: str) -> float:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        # TODO: Implement
        ...
    
    def format_formula(self, formula: WeightedCNF) -> str:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        # TODO: Implement
        ...