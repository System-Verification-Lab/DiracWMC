
from argparse import ArgumentParser, ArgumentTypeError
from .wcnf.formula import WCNFFormat, WCNF_FORMATS
from .wcnf.solvers import Solver, SolverType, SOLVERS
from .logger import log_stat

class Arguments:
    """ Processes command line arguments and stores any yielded info """

    def __init__(self):
        """ Constructor """
        self._parse_args()
        self._process_args()

    def _parse_args(self):
        """ Parse command line arguments and store them """
        parser = ArgumentParser(description="This program can be used to "
        "convert a Quantum Ising Model file to a weighted CNF file using an "
        "approximation of the Quantum Ising Model using a Classical Ising "
        "Model.")
        parser.add_argument("filename", type=str, help="The source filename of "
        "the Quantum Ising Model.")
        parser.add_argument("-o", "--output", type=str, default="output.cnf",
        help="Output filename of the generated .cnf file. Must have a .cnf "
        "extension. Defaults to output.cnf")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-s", "--solver", type=str, help="Solver to use to "
        "determine weight of generated wCNF formula. If omitted, no solver is "
        "used and weight is not determined.", choices=SOLVERS)
        group.add_argument("-f", "--format", type=str, help="Format to use for "
        "the output. This accepts the same values as --solver.",
        choices=WCNF_FORMATS)
        # parser.add_argument("-i", "--ising", action="store_true",
        # help="Generate a file with the Classical Ising Model approximation of "
        # "the Quantum Ising Model. The file will be in the same location and "
        # "have the same name as the output, but has a .json extension")
        parser.add_argument("-b", "--beta", type=float, default=1.0,
        help="Inverse temperature of the Quantum Ising Model. Defaults to 1.")
        parser.add_argument("-l", "--layers", type=lambda x:
        self._int_in_range(x, 3), default=10, help="Number of layers the "
        "Classical Ising Model uses to approximate the Quantum Ising Model.")
        parser.add_argument("-d", "--debug", action="count", help="Enables "
        "debugging information based on number of times argument is repeated: "
        "Once for exact calculation of partition function, twice for "
        "determining partition function of classical model, as well as the "
        "total weight of the wCNF formula, using brute force", default=0)
        self._args = parser.parse_args()

    def _int_in_range(self, arg: str, mn: int | None = None, mx: int | None =
    None) -> int:
        """ Checks if the given argument is a string containing an integer that
            has the given minimum and/or maximum. None means there is no
            restriction to the lower/upper bound """
        value = int(arg)
        if (mn is not None and mn > value) or (mx is not None and mx < value):
            raise ArgumentTypeError(f"{value} is in the range [{mn}, {mx}]")
        return value
    
    def _process_args(self):
        """ Process the parsed command line arguments to set defaults and extra
            values that can be determined from arguments """
        self.filename: str = self._args.filename
        self.output_filename: str = self._args.output
        self.solver_type: SolverType | None = self._args.solver
        # Solver is initialized. Output format is determined based on solver or
        # specified output format (if present)
        self.solver = None
        if self.solver_type is not None:
            self.solver = Solver.from_solver_name(self.solver_type,
            output_path=self.output_filename)
        self.output_format = "dpmc"
        match self.solver_type:
            case "cachet": self.output_format = "cachet"
            case "dpmc": self.output_format = "dpmc"
            case "tensororder": self.output_format = "cachet"
        self.solver: Solver | None
        # Output format should only be used if no solver is set
        if self._args.format is not None:
            self.output_format = self._args.format
        self.output_format: WCNFFormat
        self.beta: float = self._args.beta
        self.layers: int = self._args.layers
        self.debug_level: int = self._args.debug
        log_stat("Input filename", self.filename)
        log_stat("Inverse temperature", self.beta)
        log_stat("Approximation layers", self.layers)