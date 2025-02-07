
from typing import Iterable, Literal, get_args
from itertools import product
import json
import jsonschema

WCNFFormat = Literal["cachet", "dpmc", "json"]
WCNF_FORMATS: tuple[WCNFFormat, ...] = get_args(WCNFFormat)

WCNF_JSON_SCHEMA = {
    "type": "object",
    "required": ["num_vars", "positive_weights", "negative_weights", "clauses"],
    "additionalProperties": False,
    "properties": {
        "num_vars": {"type": "integer"},
        "positive_weights": {
            "type": "array",
            "items": {"type": ["number", "null"]},
        },
        "negative_weights": {
            "type": "array",
            "items": {"type": ["number", "null"]},
        },
        "clauses": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {"type": "integer"},
            },
        },
    },
}

class CNFFormula:
    """ A boolean formula in conjunctive normal form """

    def __init__(self, num_vars: int, *, clauses: list[list[int]] | None =
    None):
        """ Constructor, given the number of variables """
        self._num_vars = num_vars
        # Negative numbers correspond with negations
        self.clauses = [] if clauses is None else [c.copy() for c in clauses]

    def __len__(self):
        """ Get the number of variables in the CNF formula """
        return self._num_vars

    def __repr__(self):
        """ Canonical representation """
        return (f"{self.__class__.__name__}({self._num_vars!r}, clauses="
        f"{self.clauses!r})")

    def __call__(self, assignment: Iterable[bool]) -> bool:
        """ Get the truth value of the formula given some variables values """
        return self.assignment_truth(assignment)

    def assignment_truth(self, assignment: Iterable[bool]) -> bool:
        """ Get the truth value of the formula given some variable values """
        assignment = list(assignment)
        assert len(assignment) == self._num_vars
        return all(self._clause_truth(clause, assignment) for clause in
        self.clauses)

    def _clause_truth(self, clause: list[int], assignment: list[bool]) -> bool:
        """ Check if the given clause holds, given assignment of variables """
        for i in clause:
            target = i > 0
            if assignment[abs(i) - 1] == target:
                return True
        return False

class VariableWeights:
    """ Object that assigns weights to variables and their negations """

    def __init__(self, num_vars: int, *, weights: dict[int, float] | None =
    None):
        """ Constructor with a number of variables to assign weights to.
            Optionally some weights can be given in the form of a dict """
        self._num_vars = num_vars
        self._weights: list[float | None] = [None] * (num_vars * 2)
        if weights is not None:
            for var, value in weights.items():
                self.set_weight(var, value)

    def __getitem__(self, var: int) -> float | None:
        """ Get the weight of a variable (negative variables indicate negations)
            """
        self.get_weight(var)

    def __setitem__(self, var: int, value: float | None) -> float | None:
        """ Set the weight of a variable (negative variables indicate negations)
            """
        self.set_weight(var, value)

    def __len__(self) -> int:
        """ Number of variables """
        return self._num_vars

    def __repr__(self) -> str:
        """ Canonical representation """
        weights: dict[int, float] = {}
        for i in range(1, self._num_vars + 1):
            pos, neg = self.get_weight(i), self.get_weight(-i)
            if pos is not None:
                weights[i] = pos
            if neg is not None:
                weights[-i] = neg
        return (f"{self.__class__.__name__}({self._num_vars!r}, weights="
        f"{weights!r})")

    def __call__(self, assignment: Iterable[bool]) -> float:
        """ Get the weight given some assignment of variable values """
        return self.get_assignment_weight(assignment)

    def get_weight(self, var: int) -> float | None:
        """ Get the weight of a variable (negative variables indicate negations)
            """
        return self._weights[self._variable_index(var)]

    def set_weight(self, var: int, value: float | None):
        """ Set the weight of a variable (negative variables indicate negations)
            """
        self._weights[self._variable_index(var)] = value

    def get_derived_weight(self, var: int) -> float:
        """ Get the weight of a variable. If this is None return one minus the
            weight of the negation. If this is also None return 0.5 """
        if self.get_weight(var) is not None:
            return self.get_weight(var)
        if self.get_weight(-var) is not None:
            return 1.0 - self.get_weight(-var)
        return 0.5

    def get_assignment_weight(self, assignment: Iterable[bool]) -> float:
        """ Get the weight given some assignment of variable values """
        assignment = list(assignment)
        assert len(assignment) == self._num_vars
        result = 1.0
        for i, value in enumerate(assignment, 1):
            i = i if value else -i
            result *= self.get_derived_weight(i)
        return result

    def has_missing(self) -> bool:
        """ Check if there are any weights that are unset (both positive and
            negative) """
        return any(weight is None for weight in self._weights)

    def _variable_index(self, var: int):
        """ Get the index in the weights list corresponding with the given
            variable (which can be negative) """
        assert var != 0 and abs(var) <= self._num_vars
        return self._weights[var - (1 if var > 0 else 0) + self._num_vars]

class WeightedCNFFormula:
    """ CNF formula with weights assigned to positive and negative versions of
        variables """

    def __init__(self, num_vars: int, *, formula: CNFFormula | None = None,
    weights: VariableWeights | None = None):
        """ Constructor, given the number variables and optionally a formula
            and/or weights of variables. The formula and weights are not copied!
            """
        self._num_vars = num_vars
        self.formula = CNFFormula(num_vars) if formula is None else formula
        self.weights = VariableWeights(num_vars) if weights is None else weights
        assert len(self.formula) == len(self.weights) == self._num_vars

    def __len__(self) -> int:
        """ Number of variables in the weighted CNF formula """
        return self._num_vars

    def __str__(self) -> str:
        """ Convert the wCNF formula to a string in JSON format """
        return self.to_string()

    def __repr__(self) -> str:
        """ Canonical representation """
        return (f"{self.__class__.__name__}({self._num_vars!r}, formula="
        f"{self.formula!r}, weights={self.weights!r})")

    @classmethod
    def from_string(cls, text: str) -> "WeightedCNFFormula":
        """ Convert a JSON formatted string to a weighted CNF formula """
        data = json.loads(text)
        jsonschema.validate(data, WCNF_JSON_SCHEMA)
        wcnf = cls(data["num_vars"])
        assert (len(data["positive_weights"]) == len(data["negative_weights"])
        == data["num_vars"])
        wcnf.formula.clauses = data["clauses"]
        for i, value in enumerate(data["positive_weights"]):
            wcnf.weights[i] = value
        for i, value in enumerate(data["negative_weights"]):
            wcnf.weights[-i] = value
        return wcnf

    def to_string(self, output_format: WCNFFormat = "json") -> str:
        """ Convert to a formatted string. Note that only JSON formatted strings
            can be converted back to WeightedCNFFormula objects. When formatting
            is set to anything other than JSON, there should not be any missing
            weights. Solvers may also require weight normalization to work
            properly """
        if output_format != "json" and self.weights.has_missing():
            raise RuntimeError(f"Cannot format to {output_format} when there "
            f"are missing weights")
        match output_format:
            case "cachet":
                return self._to_cachet()
            case "dpmc":
                return self._to_dpmc()
            case "json":
                return self._to_json()
            case _:
                raise RuntimeError(f"Unknown output format {output_format}")

    def total_weight(self):
        """ Get the total weight over all assignments of truth values that
            satisfy the CNF formula. This is a very slow method since it uses
            brute force """
        total = 0.0
        for assignment in product((False, True), repeat=self._num_vars):
            if self.formula(assignment):
                total += self.weights(assignment)
        return total
    
    def _to_json(self) -> str:
        """ Format this object to a JSON string """
        return json.dumps({
            "num_vars": self._num_vars,
            "positive_weights": [self.weights[i] for i in range(1,
            self._num_vars + 1)],
            "negative_weights": [self.weights[-i] for i in range(1,
            self._num_vars + 1)],
            "clauses": self.formula.clauses,
        })

    def _to_cachet(self) -> str:
        """ Convert this object to a Cachet formatted string """
        text: list[str] = []
        # CNF description
        text.append(f"p cnf {self._num_vars} {len(self.formula.clauses)}")
        # Variable weights
        for i in range(1, self._num_vars + 1):
            text.append(f"w {i} {self.weights[i]}")
        # Clauses
        for clause in self.formula.clauses:
            text.append("".join(map(lambda i: str(i) + " ", clause)) + "0")
        return "\n".join(text)

    def _to_dpmc(self) -> str:
        """ Convert this object to a DPMC formatted string """
        text: list[str] = []
        # CNF description
        text.append(f"p cnf {self._num_vars} {len(self.formula.clauses)}")
        # Sum-vars
        vars_string = "".join(map(lambda i: str(i) + " ", range(1,
        self._num_vars) + 1))
        text.append(f"c p show {vars_string}0")
        # Variable weights
        for i in filter(lambda x: x != 0, range(-self._num_vars, self._num_vars
        + 1)):
            text.append(f"c p weight {i} {self.weights[i]}")
        # Clauses
        for clause in self.formula.clauses:
            text.append("".join(map(lambda i: str(i) + " ", clause)) + "0")
        return "\n".join(text)
