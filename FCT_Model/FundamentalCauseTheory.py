from __future__ import annotations
from typing import Dict, Tuple, List
from core.Theory import Theory
from repast4py import space
import random
import repast4py
import re

class FundamentalCauseTheory(Theory):

    #init is what to do when an instance is created. Anything in here is unique to each instance of the class. 
    def __init__(self, context,  mean_weekly_units:float, education:int, personal_wealth:int, power:float, prestige:float, social_connections:int, social_influence:int, space):
        self.context = context
        self.space = space
        ## FCT level parameters/attributes
        self.__mean_weekly_units: float = mean_weekly_units
        self.__education: int = education
        self.__personal_wealth: int = personal_wealth# money in the bank
        self.__total_resources: int = 0
        self.__power: float = power
        self.__prestige: float = prestige
        self.knowledge = self.__education/3
        self.__social_connections: int = social_connections
        self.__social_influence: int = social_influence
        self.successful_adaptiation = 0
        self.unsuccessful_adaptiation = 0
        
        #IMD 1 to move down between 16-30 = 0.3 ; IMD 1 to move up between 30+ = 0
        #self.deprivation_probability_dict: dict {'1': [0.02, 0.012, 0.01, 0.008, 0.005], '2': [0.013, 0.011, 0.009, 0.008, 0.008], '3': [0.01, 0.009, 0.009, 0.009, 0.007], '4': [0.01, 0.01, 0.009, 0.009, 0.009], '5': [0.007, 0.011, 0.008, 0.01, 0.016]}
        #self.deprivation_probability_list: float [[0.02, 0.012, 0.01, 0.008, 0.005], [0.013, 0.011, 0.009, 0.008, 0.008],[0.01, 0.009, 0.009, 0.009, 0.007], [0.01, 0.01, 0.009, 0.009, 0.009],[0.007, 0.011, 0.008, 0.01, 0.016]]
        
    ######################################################
    #individual agent-level situational mechanism methods

    def communicate_event(self):
        print("communicate_event_test")

    def decode_attempt(self, event):
        if event == None:
            pass
        else:
            try :
                event_value = return_decimal(event[0])
                total_resources = self.__total_resources
                if event_value/4<=total_resources:
                    self.successful_adaptiation += 1
                    self.__total_resources -= event_value/4*self.params['successful.adaptation.cost']

                    if self.knowledge < 1:
                        self.knowledge += self.params['successful.adaptation.knowlege.benefit']
                        return [event, True]
                    else:
                        return [event, True]
                else:
                    self.unsuccessful_adaptiation += 1
                    self.__total_resources -= event_value/4*self.params['unsuccessful.adaptation.cost']
                    return [event, False]
                    
            except:
                return [event, False]

    def do_situation(self):# function for the situational mechanisms
        """
        In this case, the situational mechanisms are the codes passed onto the agents to decode.
        They need to get information from the 'state' and try to decode this information.
        """
        pass

    ######################################################
    #individual agent-level action mechanism methods

    def calculate_resources(self):
        return self.knowledge + self.__personal_wealth + self.__prestige + self.__power#TODO: edit to ensure all FCT parameters are included
        # print("calculate resources test")

    def do_action(self):
        self.calculate_resources()
        #print(" strategy multiplier test: %d" % self.calculate_strategy_multiplier())

    #########################################################
    #Theory Getters
    
    def get_mean_weekly_units(self) -> float:
        return self.__mean_weekly_units
    
    def get_education(self) -> int:
        return self.__education
    
    def get_personal_wealth(self) -> int:
        return self.__personal_wealth
    
    def get_social_connections(self) -> int:
        return self.__social_connections
    
    def get_social_influence(self) -> int:
        return self.__social_influence
    
    def get_knowledge(self) -> int:
        return self.knowledge
    
    def get_total_resources(self) -> int:
        return self.__total_resources
    
    def get_successful_adaptiation(self) -> int:
        return self.successful_adaptiation
    
    def get_unsuccessful_adaptiation(self) -> int:
        return self.unsuccessful_adaptiation
    

    def get_all_theory(self) -> Dict:
        return {
            "mean_weekly_units": self.__mean_weekly_units,
            "education": self.__education,
            "personal_wealth": self.__personal_wealth,
            "knowledge": self.knowledge,
            "power": self.__power,
            "prestige": self.__prestige,
            "social_connections": self.__social_connections,
            "social_influence": self.__social_influence,
            "total_resources": self.__total_resources,
            "successful_adaptiation": self.successful_adaptiation,
            "unsuccessful_adaptiation": self.unsuccessful_adaptiation
        }
    

    #########################################################
    #Theory Setters

    def set_mean_weekly_units(self, mean_weekly_units: float):
        self.__mean_weekly_units = mean_weekly_units

    def set_education(self, education: int):
        self.__education = education

    def set_personal_wealth(self, personal_wealth: int):
        self.__personal_wealth = personal_wealth

    def set_social_connections(self, social_connections: int):
        self.__social_connections = social_connections

    def set_social_influence(self, social_influence: int):
        self.__social_influence = social_influence

    def set_params(self, params):
        self.params = params


def return_decimal(value):
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    
    if re.match("^[01]+$", value):
        return int(value, 2)
    elif re.match("^[0-9a-fA-F]+$", value):
        return int(value, 16)
    else:
        raise ValueError("Not a binary or hex string")
