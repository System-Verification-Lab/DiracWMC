
from .formula import WeightedCNFFormula
from ..logger import log_info, log_stat, log_warning
import os
from subprocess import Popen, PIPE
from time import time
from typing import Literal, get_args
from dataclasses import dataclass

SolverType = Literal["cachet", "dpmc", "tensororder"]
SOLVERS: tuple[SolverType, ...] = get_args(SolverType)
SOLVER_TIMEOUT = 15

@dataclass
class SolverResult:
    """ An object containing information about a solver run """

    success: bool = False
    runtime: float = -1.0
    total_weight: float = 0.0

class Solver:
    """ Generic solver interface """

    def __init__(self, *, output_path: str = "output.cnf", timeout: float =
    15.0):
        """ Constructor. An output file path can be given to output the produced
            .cnf file to. The timeout is in seconds and is a timeout of the
            entire process, so not just the solver runtime """
        self.output_path = output_path
        self.timeout = timeout

    @classmethod
    def from_solver_name(self, solver_type: SolverType, *args, **kwargs) -> (
    "Solver"):
        """ Get a specific solver interface given by the solver name. Other
            arguments for the solver constructor can be passed as well """
        match solver_type:
            case "cachet": return CachetSolver(*args, **kwargs)
            case "dpmc": return DPMCSolver(*args, **kwargs)
            case "tensororder": return TensorOrderSolver(*args, **kwargs)
        raise RuntimeError(f"Unsupported solver type {solver_type}")

    def run_solver(self, formula: WeightedCNFFormula) -> SolverResult:
        """ Run the solver on the given weighted CNF formula and return an
            object with several statistics, including total weight and runtime
            """
        raise NotImplementedError

    def calculate_weight(self, formula: WeightedCNFFormula) -> float:
        """ Output the given formula to the specified output file and calculate
            the total weight using the solver. Returns the total weight """
        log_info("Creating output file...")
        self.make_output_file(formula)
        log_info("Running solver...")
        self._runtime = None
        start = time()
        result = self.calculate_from_file(self._output_path)
        end = time()
        log_stat("Solver output", str(result))
        # Only measure runtime if this is not done in the calculate_from_file
        # function
        if self._runtime is None:
            self._runtime = end - start
        log_stat("Total runtime", f"{end - start:.3f} s")
        return result

class DPMCSolver(Solver):
    """ Solver interface for the DPMC solver """

    def run_solver(self, formula: WeightedCNFFormula) -> SolverResult:
        """ Run the solver on the given weighted CNF formula and return an
            object with several statistics, including total weight and runtime
            """
        ...

    def _create_file(self):
        """ Create the output file to pass to the solver """
        ...

    def _calculate_from_file(self) -> float:
        """ Calculate total weight of wCNF formula in the given .cnf file """
        cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..",
        "..", "solvers", "DPMC")
        filepath = os.path.join(os.getcwd(), self.output_path)
        infile = open(filepath, "r")
        p1 = Popen(["./lg/build/lg", "./lg/solvers/flow-cutter-pace17/"
        "flow_cutter_pace17 -p 100"], cwd=cwd, stdout=PIPE, stdin=infile)
        p2 = Popen(["./dmc/dmc", f"--cf={filepath}"], cwd=cwd, stdout=PIPE,
        stdin=p1.stdout)
        output, _ = p2.communicate(timeout=SOLVER_TIMEOUT)
        result = output.decode("utf-8")
        for line in result.split("\n"):
            if line.startswith("c s exact double prec-sci"):
                return float(line.split()[-1])
        raise Exception("Could not find result of DPMC. Something must have "
        "gone wrong while running it")
    
    def format_formula(self, formula: WeightedCNFFormula) -> str:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        return formula.to_string("dpmc")

class CachetSolver(Solver):
    """ Solver interface for the Cachet solver """

    def calculate_from_file(self, filename: str) -> float:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..",
        "..", "solvers", "cachet")
        filepath = os.path.join(os.getcwd(), filename)
        p = Popen(["./cachet", filepath], cwd=cwd, stdout=PIPE)
        output, _ = p.communicate(timeout=SOLVER_TIMEOUT)
        result = output.decode("utf-8")
        for line in result.split("\n"):
            if line.startswith("Satisfying probability"):
                return float(line.split()[-1])
        raise Exception("Could not find result of Cachet. Something must have "
        "gone wrong while running it")
    
    def format_formula(self, formula: WeightedCNFFormula) -> str:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        return formula.to_string("cachet")
    
class TensorOrderSolver(Solver):
    """ Solver interface for the TensorOrder solver """

    def calculate_from_file(self, filename: str) -> float:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..",
        "..", "solvers", "TensorOrder")
        filepath = os.path.join(os.getcwd(), filename)
        infile = open(filepath, "r")
        p = Popen(["docker", "run", "-i", "tensororder:latest", "python",
        "/src/tensororder.py", "--planner=factor-Flow",
        "--weights=cachet"], cwd=cwd, stdout=PIPE, stdin=infile)
        output, _ = p.communicate(timeout=SOLVER_TIMEOUT)
        result = output.decode("utf-8")
        time_taken = count = None
        for line in result.split("\n"):
            if line.startswith("Total Time:"):
                time_taken = float(line.split()[-1])
            if line.startswith("Count:"):
                count = float(line.split()[-1])
        if count is None:
            raise Exception("Could not find result of TensorOrder. Something "
            "must have gone wrong while running it")
        if time_taken is not None:
            log_stat("TensorOrder measured time", f"{time_taken:.3f} s")
            self._runtime = time_taken
        else:
            log_warning("TensorOrder measured time not found")
        return count
    
    def format_formula(self, formula: WeightedCNFFormula) -> str:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        return formula.to_string("cachet")