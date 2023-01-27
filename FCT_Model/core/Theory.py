from __future__ import annotations
from typing import Dict, Tuple, List
from abc import abstractmethod, ABCMeta

from .MicroAgent import MicroAgent

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