from __future__ import annotations
from typing import Dict, Tuple, List

import repast4py

from core.MicroAgent import MicroAgent

# TODO: Inherit MicroAgent
class FCT_Agent(MicroAgent):
    TYPE = 1
    def __init__(self, id:int, rank:int, agent_type:int, threshold:float, space):
        super().__init__(id=id, type=FCT_Agent.TYPE, rank=rank)

        # TODO: define 3 variables: the type of the agent, the satisfied status, the threshold
        self.__agent_type: int = agent_type
        self.__is_satisfied: bool = False
        self.__threshold: float = threshold

        self.space = space

    # This has been renamed to differentiate from the TYPE which is part of Repast4Py's 
    def get_agent_type(self) -> int:
        return self.__agent_type

    def get_satisfied_status(self) -> bool:
        return self.__is_satisfied

    def get_threshold(self) -> float:
        return self.__threshold

    def set_satisfied_status(self, satisfied_status:bool):
        self.__is_satisfied = satisfied_status

    # TODO: define move() function
    def move(self):
        # TODO: move to a random empty position
        # get this agents location
        location = self.space.get_location(self)
        # get the bounds of the environment
        local_bounds = self.space.get_local_bounds()
        # find a random empty position.
        # Note this will loop forever if the board is full (but this should be prevented by an early check)
        rng = repast4py.random.default_rng
        random_location = self.space.get_random_local_pt(rng)
        while self.space.get_num_agents(random_location) != 0:
            random_location = self.space.get_random_local_pt(rng)
        # Move to the new location
        self.space.move(self, random_location)

    def save(self) -> Tuple:
        """ Save the state of this FCT_Agent as a Tuple.
        
        Used to move FCT_Agent between Ranks in Repast4py.
        This is analogous to FCT_AgentPackage::serialize int he RepastHPC implementation

        Returns:
            The saved state of this FCT_Agent
        """
        return (self._id, self._mediator, self.__agent_type, self.__is_satisfied, self.__threshold, self.space)
