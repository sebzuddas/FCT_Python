from __future__ import annotations
from typing import Dict, Tuple, List
from abc import abstractmethod, ABCMeta

from .MicroAgent import MicroAgent

class Theory(metaclass=ABCMeta):
    
    def __init__(self):
        self._agent: MicroAgent = None

    def set_agent(self, agent:MicroAgent):
        self._agent = agent
    """
    The @abstractmethod decorator is used to indicate that a method is
    abstract and must be implemented by any concrete subclass of the abstract class.
    An abstract method is a method that is declared in the abstract class but
    does not have an implementation
    """

    @abstractmethod
    def do_situation(self):
        pass

    @abstractmethod
    def do_action(self):
        pass

    @abstractmethod
    def communicate_event(self):
        pass


