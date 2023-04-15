from __future__ import annotations
from typing import Dict, Tuple, List
from abc import abstractmethod, ABCMeta

class Regulator(metaclass=ABCMeta):

    def __init__(self):
        pass

    # update the adjustment level variable (private).
	# Modeller should write getter function(s) to access to adjustment level variable, depending on the data structure (it can be a value or array)
    @abstractmethod
    def update_adjustment_level(self):
        pass
