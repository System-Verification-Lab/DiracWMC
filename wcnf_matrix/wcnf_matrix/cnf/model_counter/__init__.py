
from .model_counter import ModelCounter, ModelCounterResult
from .dpmc import DPMC
from .cachet import Cachet

default_model_counter = DPMC

def set_model_counter(model_counter: type[ModelCounter]):
    """ Change the default model counter used """
    global default_model_counter
    default_model_counter = model_counter