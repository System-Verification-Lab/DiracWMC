
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Iterator
from ..cnf import CNF
from ..weights import WeightFunction

@dataclass
class ModelCounterResult:
    """ An object containing information about a model counter run """

    success: bool
    runtime: float = -1.0
    model_count: float = 0.0

    def __str__(self) -> str:
        """ String representation for a formatted string showing results """
        items = {
            "Success": str(self.success),
            "Runtime": f"{self.runtime:.2f} s",
            "Total weight": f"{self.total_weight:.10f}",
        }
        output = []
        for key, value in items.items():
            output.append((key + ":").ljust(15) + " " + value)
        return "\n".join(output)



class ModelCounter(ABC):
    """ Base class of model counters """

    def __init__(self, *, timeout: float = 15.0, show_log: bool = False):
        """ Constructor. A timeout in seconds can be given and logging can be
            enabled """
        self._timeout = timeout
        self._show_log = show_log

    @abstractmethod
    def model_count(self, cnf: CNF, weight_func: WeightFunction) -> (
    ModelCounterResult):
        """ Get the model count of the given CNF formula with respect to the
            given weight function """
        pass

    @classmethod
    @abstractmethod
    def is_available(self) -> bool:
        """ Check if the model counter is available to run """
        pass

    def batch_model_count(self, *problems: tuple[CNF, WeightFunction]) -> (
    Iterator[ModelCounterResult]):
        """ Run the model counter on a batch of problems. Returns an iterator
            over all results in order """
        # NOTE: Default implementation calls model_count repeatedly
        for cnf, weight_func in problems:
            yield self.model_count(cnf, weight_func)