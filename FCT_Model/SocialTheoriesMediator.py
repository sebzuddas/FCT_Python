from __future__ import annotations
from typing import List

from core.Theory import Theory
from core.TheoryMediator import TheoryMediator

from FundamentalCauseTheory import FundamentalCauseTheory
from FCT_Agent import FCT_Agent
import numpy as np
from numpy import random

class SocialTheoriesMediator(TheoryMediator):

    # defines the constructor, calling the parent class constructor
    def __init__(self, theory_list:List[Theory]):
        # Call the parent class constructor
        super().__init__(theory_list)
        # We require one theory in the theory list for member methods, abort if that is not the case.
        if len(self._theory_list) == 0: 
            raise Exception(f"{__class__.__name__} require a theory_list with length > 0")

    
    def mediate_situation(self):
        # trigger situation mechanisms
        self._theory_list[0].do_situation()
        
    
    def mediate_action(self):
        # trigger action mechanisms
        self._theory_list[0].do_action()
        self.agent.move()

        consumption = round(self.agent.drink(self._theory_list[0].get_mean_weekly_units()), 2)
        if consumption > 490:
            ld_50 = np.random.choice([0, 1])
            if ld_50 == 1:
                self.agent.kill()
        elif(self.agent.get_agent_age()>100):
            self.agent.kill()
        self.agent.absolute_risk(consumption)
        
        #get the deprivation quintile
        # if self._theory_list[0].get_deprivation_quintile():
        #     self.agent.get_deprivation_quintile()

