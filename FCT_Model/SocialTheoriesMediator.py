from __future__ import annotations
from typing import List

from core.Theory import Theory
from core.TheoryMediator import TheoryMediator

from FundamentalCauseTheory import FundamentalCauseTheory
from FCT_Agent import FCT_Agent
import numpy as np
from numpy import random

# TODO: inherit TheoryMediator
class SocialTheoriesMediator(TheoryMediator):

    # TODO: define the constructor, calling the parent class constructor
    def __init__(self, theory_list:List[Theory]):
        # Call the parent class constructor
        super().__init__(theory_list)
        # We require one theory in the theory list for member methods, abort if that is not the case.
        if len(self._theory_list) == 0: 
            raise Exception(f"{__class__.__name__} require a theory_list with length > 0")

    # TODO: override mediate_situation()
    def mediate_situation(self):
        # TODO: trigger situation mechanisms
        self._theory_list[0].do_situation()

        # TODO: get the satisfaction value from the Theory object
        updated_satisfaction:bool = self._theory_list[0].get_satisfied_status()

        # TODO: because there is only one theory, pass satisfaction value to the agent
        self.agent.set_satisfied_status(updated_satisfaction)
        

    # TODO override mediate_action()
    def mediate_action(self):
        # TODO: trigger action mechanisms
        self._theory_list[0].do_action()
        self.agent.move()

        consumption = round(self.agent.drink(self._theory_list[0].get_mean_weekly_units()), 2)
        if consumption > 490:
            ld_50 = np.random.choice([0, 1])
            if ld_50 == 1:
                self.agent.kill()
                

        self.agent.absolute_risk(consumption)

        


        # TODO: if the agent intends to move, perform the move action
        if self._theory_list[0].get_moving_intention():
            pass
        
        #get the deprivation quintile
        # if self._theory_list[0].get_deprivation_quintile():
        #     self.agent.get_deprivation_quintile()

