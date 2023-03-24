#! /usr/bin/env python3
from __future__ import annotations
from typing import Tuple

from abc import abstractmethod, ABCMeta
import numpy as np
from repast4py import core
import repast4py


class MicroAgent(repast4py.core.Agent, metaclass=ABCMeta):

    @property
    @abstractmethod
    def TYPE(cls) -> int:
        """ The type component used within repast4py's uids, which should be unique per agent type
        This is annotated as @proprerty @abstractmethod to enforce derived classes to set a value, though the runtime error is not ideal
        """
        raise NotImplementedError

    def __init__(self, id: int, rank:int, type:int = None):
        # Call the parent class constructor, i.e. what makes this a repast4py agent
        # Use the type of the agent, but allow it to be over-written by derived classes
        if type is None:
            type = cls.TYPE 
        super().__init__(id=id, type=type, rank=rank)
        # self.id is the id from the rank on which it was generated
        # self.type is the integer type of the agent within the simulation. I..e MicroAgent.TYPE, which should be distinct from a DerivedMicroAgent.TYPE.
        # self.rank is the rank from which this agent was generated
        # self.uid is the unique 3-tuple of (id, type, rank)
        self._mediator = None

    def get_id(self):
        return self._id

    def set(self, current_rank):
        self.current_rank = current_rank
        pass

    def set_mediator(self, mediator: TheoryMediator):
        self._mediator = mediator
    

    #TODO: rename to call_situation
    def call_situation(self):
        if self._mediator is not None:
            self._mediator.mediate_situation()


    #TODO: rename to call_action
    def call_action(self):
        if self._mediator is not None:
            self._mediator.mediate_action()

    def save(self):
        """ Save the state of this MicroAgent as a Tuple.
        
        Used to move MicroAgents between Ranks in Repast4py.
        This is analogous to AgentPackage::serialize int he RepastHPC implementation

        Returns:
            The saved state of this MicroAgent
        """
        return (self._id, self._mediator)

def restore_agent(agent_data:Tuple):
    """ 
    Repast4py uses save() and restore_agent to migrate agents between ranks.
    The MBSSM core is only implemented for single-rank simulations, i.e. this method is not implemented.
    """
    raise NotImplementedError

# Include this at the end of the file to avoid circular import
from .TheoryMediator import TheoryMediator
