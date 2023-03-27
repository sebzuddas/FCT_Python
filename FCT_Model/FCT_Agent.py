"""
List of todos
#TODO: change from Schelling to FCT relevant stuff
#TODO: store change in deprivation quintile for each agents - make it a dataclass?
#TODO: 

List of bugs

List of questions

"""

from __future__ import annotations
from typing import Dict, Tuple, List

import repast4py

from numpy import random


from core.MicroAgent import MicroAgent

# TODO: Inherit MicroAgent
class FCT_Agent(MicroAgent):
    TYPE = 1
    #WITH DISCRETE SPACE
    #def __init__(self, type:int, id:int, rank:int, deprivation_quintile:int, sex: bool, age: int, drinking_status: int,  space):

    def __init__(self, id:int, type:int, rank:int, deprivation_quintile:int, sex: int, age: int, drinking_status: int, space):
        super().__init__(id=id, type=FCT_Agent.TYPE, rank=rank)

        self.__is_satisfied: bool = False
        self.__type = type
        self.__rank: int = rank
        self.__deprivation_quintile: int = deprivation_quintile
        self.sex = sex
        self.age = age
        self.drinking_status = drinking_status
        self.space = space
        #self.deprivation_probability_list: float [[0.3, 0], [0.3, 0], [0.4, 0], [0, 0.4], [0, 0.6]]

    ##################################################################
    #Agent Getters

    def get_agent_id(self) -> int:
        return self.id
    
    def get_agent_rank(self) -> int:
        return self._rank
    
    def get_deprivation_quintile(self) -> int:
        return self.__deprivation_quintile
    
    def get_agent_sex(self) -> int:
        return self.sex
    
    def get_agent_age(self) -> int:
        return self.age
    
    def get_agent_drinking_status(self) -> bool:
        return self.drinking_status
    
    def get_satisfied_status(self) -> bool:
        return self.__is_satisfied
    
    def get_space(self):
        return self.space
    
    
    
    ##################################################################
    #Agent Setters

    def set_deprivation_quintile(self, deprivation_quintile: int):
        self.__deprivation_quintile = deprivation_quintile

    def set_agent_age(self, age: int):
        self.age = age
    
    def set_agent_drinking_status(self, drinking_status: bool):
        self.drinking_status = drinking_status

    def set_satisfied_status(self, satisfied_status:bool):
        self.__is_satisfied = satisfied_status

    def set_space(self, space):
        self.space = space


    ####################################################################
    #Agent Methods

    def generate_binary_string(n):
        # Generate a random number with n bits
        number = random.getrandbits(n)
        # Convert the number to binary
        binary_string = format(number, '0b')
        return binary_string

    def move(self):
        #TODO: restrict movements depending on deprivation quintile
        #move to a random empty position:
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

    def absolute_risk(self, beta):
        consumption = self.get_agent_drinking_status()
        if consumption == 0:
            return 0
        else:
            return beta * consumption


    ####################################################################
    #Agent Package Methods
    def save(self) -> Tuple:
        """ Save the state of this FCT_Agent as a Tuple.
        
        Used to move FCT_Agent between Ranks in Repast4py.
        This is analogous to FCT_AgentPackage::serialize int he RepastHPC implementation

        Returns:
            The saved state of this FCT_Agent
        """
        return (self._id, self._mediator, self.sex, self.__is_satisfied, self.__deprivation_quintile, self.space)
    
    def update(self, data:bool):
        """ to restore the agent after it has change ranks"""
        pass
