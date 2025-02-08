
from .formula import WeightedCNFFormula
from ..logger import log_info, log_warning, log_stat
import os
from subprocess import Popen, PIPE, TimeoutExpired
from time import time
from typing import Literal, get_args
from dataclasses import dataclass

SolverType = Literal["cachet", "dpmc", "tensororder"]
SOLVERS: tuple[SolverType, ...] = get_args(SolverType)

@dataclass
class SolverResult:
    """ An object containing information about a solver run """

    success: bool
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
    def from_solver_name(cls, solver_type: SolverType, *args, **kwargs) -> (
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

class DPMCSolver(Solver):
    """ Solver interface for the DPMC solver """

    def run_solver(self, formula: WeightedCNFFormula) -> SolverResult:
        """ Run the solver on the given weighted CNF formula and return an
            object with several statistics, including total weight and runtime
            """
        log_info("Creating output file...")
        self._create_file(formula)
        log_info("Running solver...")
        return self._calculate_from_file()

    def _create_file(self, formula: WeightedCNFFormula):
        """ Create the output file to pass to the solver """
        with open(self.output_path, "w") as f:
            f.write(formula.to_string("dpmc"))

    def _calculate_from_file(self) -> SolverResult:
        """ Calculate total weight of wCNF formula in the given .cnf file """
        cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..",
        "..", "solvers", "DPMC")
        filepath = os.path.join(os.getcwd(), self.output_path)
        infile = open(filepath, "r")
        p1 = Popen(["./lg/build/lg", "./lg/solvers/flow-cutter-pace17/"
        "flow_cutter_pace17 -p 100"], cwd=cwd, stdout=PIPE, stdin=infile)
        p2 = Popen(["./dmc/dmc", f"--cf={filepath}"], cwd=cwd, stdout=PIPE,
        stdin=p1.stdout)
        start = time()
        try:
            output, _ = p2.communicate(timeout=self.timeout)
        except TimeoutExpired:
            return SolverResult(False)
        end = time()
        result = output.decode("utf-8")
        for line in result.split("\n"):
            if line.startswith("c s exact double prec-sci"):
                weight = float(line.split()[-1])
                log_stat("Solver output", weight)
                return SolverResult(True, end - start, weight)
        return SolverResult(False)

class CachetSolver(Solver):
    """ Solver interface for the Cachet solver """

    def run_solver(self, formula: WeightedCNFFormula) -> SolverResult:
        """ Run the solver on the given weighted CNF formula and return an
            object with several statistics, including total weight and runtime
            """
        formula = formula.copy()
        formula.weights.add_missing()
        factor = formula.weights.normalize()
        if factor in (float("inf"), float("-inf"), 0.0):
            log_warning(f"Cachet failed because normalization factor is "
            f"{factor}")
            return SolverResult(False)
        log_stat("wCNF normalization factor", factor)
        log_info("Creating output file...")
        self._create_file(formula)
        log_info("Running solver...")
        result = self._calculate_from_file()
        if result.success:
            result.total_weight *= factor
        return result
    
    def _create_file(self, formula: WeightedCNFFormula):
        """ Create the output file to pass to the solver """
        with open(self.output_path, "w") as f:
            f.write(formula.to_string("cachet"))

    def _calculate_from_file(self) -> SolverResult:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..",
        "..", "solvers", "cachet")
        filepath = os.path.join(os.getcwd(), self.output_path)
        p = Popen(["./cachet", filepath], cwd=cwd, stdout=PIPE)
        try:
            start = time()
            output, _ = p.communicate(timeout=self.timeout)
            end = time()
        except TimeoutExpired:
            return SolverResult(False)
        result = output.decode("utf-8")
        for line in result.split("\n"):
            if line.startswith("Satisfying probability"):
                weight = float(line.split()[-1])
                log_stat("Solver output", weight)
                return SolverResult(True, end - start, weight)
        return SolverResult(False)

class TensorOrderSolver(Solver):
    """ Solver interface for the TensorOrder solver """

    def run_solver(self, formula: WeightedCNFFormula) -> SolverResult:
        """ Run the solver on the given weighted CNF formula and return an
            object with several statistics, including total weight and runtime
            """
        log_info("Creating output file...")
        self._create_file(formula)
        log_info("Running solver...")
        return self._calculate_from_file()
    
    def _create_file(self, formula: WeightedCNFFormula):
        """ Create the output file to pass to the solver """
        with open(self.output_path, "w") as f:
            f.write(formula.to_string("cachet"))

    def _calculate_from_file(self) -> float:
        """ Convert the given wCNF formula to the format that the solver can use
            """
        cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..",
        "..", "solvers", "TensorOrder")
        filepath = os.path.join(os.getcwd(), self.output_path)
        infile = open(filepath, "r")
        p = Popen(["docker", "run", "-i", "tensororder:latest", "python",
        "/src/tensororder.py", "--planner=factor-Flow",
        "--weights=cachet"], cwd=cwd, stdout=PIPE, stdin=infile)
        try:
            output, _ = p.communicate(timeout=self.timeout)
        except TimeoutExpired:
            return SolverResult(False)
        result = output.decode("utf-8")
        time_taken = count = None
        for line in result.split("\n"):
            if line.startswith("Total Time:"):
                time_taken = float(line.split()[-1])
            if line.startswith("Count:"):
                count = float(line.split()[-1])
                log_stat("Solver output", count)
        if count is None:
            return SolverResult(False)
        if time_taken is None:
            time_taken = -1.0
            log_warning("TensorOrder measured time not found")
        return SolverResult(True, time_taken, count)