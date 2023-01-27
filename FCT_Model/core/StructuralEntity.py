
from __future__ import annotations
from typing import Dict, Tuple, List
from abc import abstractmethod, ABCMeta

import repast4py

from .Regulator import Regulator
from .MicroAgent import MicroAgent

# ABCMeta is how to define abstract base classes in python
class StructuralEntity(metaclass=ABCMeta):

    def __init__(self):
        self._regulatorList: List[Regulator] = []
        self._transformational_interval: int = 0

    # Python does not support overloaded constructors, classmethod is a nice alternative
    @classmethod
    def ctor(cls, regulator_list: List[Regulator], transformational_interval: int) -> StructuralEntity:
        instance = cls()
        instance._regulator_list = regulator_list
        instance._transformational_interval =  transformational_interval
        return instance

    @abstractmethod
    def do_transformation(self):
        pass

class Theory(metaclass=ABCMeta):
    
    def __init__(self):
        self._agent: MicroAgent = None

    def set_agent(self, agent:MicroAgent):
        self._agent = agent

    @abstractmethod
    def do_situation(self):
        pass

    @abstractmethod
    def do_action(self):
        pass
