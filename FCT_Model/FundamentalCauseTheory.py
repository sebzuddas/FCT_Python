from __future__ import annotations
from typing import Dict, Tuple, List
from core.Theory import Theory
from repast4py import space
import repast4py


# TODO: inherit Theory
class FundamentalCauseTheory(Theory):

    #init is what to do when an instance is created. Anything in here is unique to each instance of the class. 
    def __init__(self, context,  mean_weekly_units:float, education:int, personal_wealth:int, social_connections:int, social_influence:int, space):
        self.context = context
        self.space = space
        self.__social_influence: int = social_influence

        #TODO: Why are these not being worked out here?
        ## FCT level parameters/attributes
        
        self.__mean_weekly_units: float = mean_weekly_units
        self.__education: int = education
        self.__personal_wealth: int = personal_wealth

        #TODO these two theory level parameters are determined by other classes. How to manage?
        self.__social_connections: int = social_connections
        self.__age_group: int

        # TODO: define a variable satisfaction status
        self.__is_satisfied:bool = False
        # TODO: define a variable for moving decision
        self.__moving_intention:bool = False
        self.strategy_multiplier: float
        
        
        #IMD 1 to move down between 16-30 = 0.3 ; IMD 1 to move up between 30+ = 0
        #self.deprivation_probability_dict: dict {'1': [0.02, 0.012, 0.01, 0.008, 0.005], '2': [0.013, 0.011, 0.009, 0.008, 0.008], '3': [0.01, 0.009, 0.009, 0.009, 0.007], '4': [0.01, 0.01, 0.009, 0.009, 0.009], '5': [0.007, 0.011, 0.008, 0.01, 0.016]}
        # self.deprivation_probability_list: float [[0.02, 0.012, 0.01, 0.008, 0.005], [0.013, 0.011, 0.009, 0.008, 0.008],[0.01, 0.009, 0.009, 0.009, 0.007], [0.01, 0.01, 0.009, 0.009, 0.009],[0.007, 0.011, 0.008, 0.01, 0.016]]
        
    ######################################################
    #individual agent-level situational mechanism methods

    def communicate_event(self):

        
        print("communicate_event_test")

    def do_situation(self):# function for the situational mechanisms
        """
        In this case, the situational mechanisms are the codes passed onto the agents to decode. 
        They need to get information from the 'state' and try to decode this information.
        """
        center = self.space.get_location(self._agent)
        # Count similar agents in the local 2D grid moore neighbourhood
        similar_count = 0
        neighbour_count = 0
        # Repast4Py does not include repast::Moore2DQueryGrid
        rel_neighbourhood = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)] # excludes center
        local_bounds = self.space.get_local_bounds()
        xmax = local_bounds.xmin + local_bounds.xextent
        ymax = local_bounds.ymin + local_bounds.yextent
        
        
        for rel_loc in rel_neighbourhood:
            other_loc = repast4py.space.DiscretePoint(center.x + rel_loc[0], center.y + rel_loc[1])
            # Check the relative loc is in bounds
            if other_loc.x >= local_bounds.xmin and other_loc.y >= local_bounds.ymin and other_loc.x < xmax and other_loc.y < ymax:
                # Get the first (and only) agent at the other location, if there is one
                other_agent = self.space.get_agent(other_loc)
                if other_agent is not None:
                    neighbour_count += 1
                    # TODO: increase the count if 2 agents are the same type
                    if other_agent.get_agent_sex() == self._agent.get_agent_sex():
                        similar_count += 1

        # TODO: Change the satisfied status
        
        self.__is_satisfied = True


    ######################################################
    #individual agent-level action mechanism methods
    #
    def moving_intention(self):
        # TODO: if not satisfied, moving intention =True else =False
        self.__moving_intention = not self.__is_satisfied
        

    def calculate_resources(self):
        print("calculate resources test")

    def calculate_strategy_multiplier(self):
        #TODO: finish strat multiplier
        self.strategy_multiplier = float(self.__education + self.__deprivation_quintile + self.__personal_wealth + self.__mean_weekly_units)
        return self.strategy_multiplier
    


    # TODO: override do_action()
    def do_action(self):
        
        self.moving_intention()


        #self.calculate_strategy_multiplier()
        
        #print(" strategy multiplier test: %d" % self.calculate_strategy_multiplier())


    def get_satisfied_status(self) -> bool:
        return self.__is_satisfied

    def get_moving_intention(self) -> bool:
        return self.__moving_intention
