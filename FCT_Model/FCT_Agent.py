from __future__ import annotations
from typing import Dict, Tuple, List

import repast4py

import numpy as np
import random
import csv
from typing import Any, Dict




from core.MicroAgent import MicroAgent

class FCT_Agent(MicroAgent):
    TYPE = 1
    def __init__(self, id:int, type:int, rank:int, deprivation_quintile:int, sex: int, age: int, drinking_status: int, target_connections: int, space):
        super().__init__(id=id, type=FCT_Agent.TYPE, rank=rank)

        self.__type: int = type
        self.__rank: int = rank
        self.__deprivation_quintile: int = deprivation_quintile
        self.sex = sex
        self.age = age
        self.drinking_status = drinking_status
        self.target_connections = target_connections
        self.space = space
        self.params = None
        

        #Tracking Variables
        self.death_count = 0
        self.original_dq = None
        # self.current_dq = None
        # self.moved_down_dq = None
        # self.moved_up_dq = None
        self.abs_risk = 0

        # Arrays and dictionaries
        self.connections_array = []
        self.received_events = []
        self.solved_events = []
        self.unsolved_events = []
        self.theory_dict = {}

        
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
    
    def get_target_connections(self) -> int:
        return self.target_connections
    
    def get_target_connections_array(self) -> List[int]:
        return self.connections_array
    
    def get_agent_solved_events(self) -> List[int]:
        return self.solved_events
    
    def get_space(self):
        return self.space
    
    def get_theory_dict(self) -> Dict[str, int]:
        return self.theory_dict
    
    def get_random_event(self):

        # rng = np.random.default_rng(seed=1)

        if len(self.unsolved_events) != 0:# ensure theres a list of events
            i=0
            while i<len(self.unsolved_events):
                chosen_event = random.choice(self.unsolved_events)# choose a random event
                if not chosen_event[1]: # check again that the event hasn't been solved. 
                    return chosen_event[0] # return the event
                else: 
                    chosen_event = random.choice(self.unsolved_events)# choose a random event
        
    

    


    
    ##################################################################
    #Agent Setters
    def set_params(self, params):
        self.params = params

    def set_deprivation_quintile(self, deprivation_quintile: int):
        self.__deprivation_quintile = deprivation_quintile

    def set_agent_age(self, age: int):
        self.age = age
    
    def set_agent_drinking_status(self, drinking_status: bool):
        self.drinking_status = drinking_status

    def set_target_connections(self, target_connections: int):
        self.target_connections = target_connections

    def append_connections_array(self, connection: int):
        self.connections_array.append(connection)

    def set_space(self, space):
        self.space = space

    def handle_event(self, event, is_solved):
        event = tuple(event)  # Convert event to a tuple

        if not is_solved:#if the returned event is deemed unsolved
            # Add the event to received_events and unsolved_events
            self.received_events.append([event, is_solved])
            self.unsolved_events.append([event, is_solved])# add the event to the unsolved events list TODO: fix
            
        if is_solved:
            # If the event is solved, update the lists accordingly
            self.solved_events.append(event)

            # Remove [event, False] from received_events
            self.received_events = [entry for entry in self.received_events if entry != [event, False]]

            # Remove all instances of [event, False] from unsolved_events
            self.unsolved_events = [entry for entry in self.unsolved_events if entry != [event, False]]

            # Add [event, True] to received_events
            self.received_events.append([event, True])

    def set_theory_array(self, theory):
        self.theory_dict.update(theory)

    def set_params(self, params):
        self.params = params


    ####################################################################
    #Agent Methods
    
    def drink(self, weekly_units):
        amount = self.drinking_status*weekly_units
        # print(amount)
        return amount
    
    def absolute_risk(self, consumption):

        if self.sex == 0:
            beta = self.params['beta.modifier.female']
        else:
            beta = self.params['beta.modifier.male']


        # consumption = self.get_agent_drinking_status()
        if consumption == 0:
            #print(consumption)
            self.abs_risk = 0
            return 0
        else:

            self.abs_risk = 100 * beta * (consumption-0.5)

            return self.abs_risk
    
    def kill(self):
        
        self.death_count += 1
        print(self.death_count, self.age)
        self.set_agent_age(18)

        return True

    def move(self):

        dq = self.__deprivation_quintile
        random_dq_point = get_random_location(dq)
        #print(random_dq_point, dq)
        # exit()
        random_location = repast4py.space.DiscretePoint(random_dq_point[1], random_dq_point[0])
          
        while self.space.get_num_agents(random_location) != 0:
            random_dq_point = get_random_location(dq)
            random_location = repast4py.space.DiscretePoint(random_dq_point[1], random_dq_point[0])
            #print(random_location, '\n', self.space.get_num_agents(random_location))
            # Move to the new location
        self.space.move(self, random_location)
 
    def get_agent_location(self):
        location_object = self.space.get_location(self)
        coords = location_object.coordinates
        return (coords[0], coords[1])

        # return self.space.get_location(self)
    
    def interpret_event(self, event):
        self.unsolved_events.append([event, False])
        self.received_events.append([event, False])
        #print(self.received_events, self.get_id())

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

def get_random_location(deprivation_quintile):
        #, file_location = 'FCT_Python/FCT_Model/props/area/DQ_areas.csv'
        #rng = np.random.default_rng(seed=rng_seed)  # create a default Generator instance
        #pos_rand = np.random.default_rng().choice(DQ_1_coords, replace=False)
        
        match deprivation_quintile:
            case 0:
                DQ_1_coords = find_all_cell_coordinates('1')
                pos_rand = np.random.default_rng().choice(DQ_1_coords, replace=False)
                return (pos_rand)
            case 1:
                DQ_2_coords = find_all_cell_coordinates('2')
                pos_rand = np.random.default_rng().choice(DQ_2_coords, replace=False)
                return (pos_rand)
            case 2:
                DQ_3_coords = find_all_cell_coordinates('3')
                pos_rand = np.random.default_rng().choice(DQ_3_coords, replace=False)
                return (pos_rand)
            case 3:
                DQ_4_coords = find_all_cell_coordinates('4')
                pos_rand = np.random.default_rng().choice(DQ_4_coords, replace=False)
                return (pos_rand)
            case 4:
                DQ_5_coords = find_all_cell_coordinates('5')
                pos_rand = np.random.default_rng().choice(DQ_5_coords, replace=False)
                return (pos_rand)
            case _:
                raise ValueError("Deprivation quintile must be between 0 and 4")

def find_all_cell_coordinates(target_value):
    csv_file = 'FCT_Model/props/area/DQ_areas.csv'
    coordinates = []
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        for row_num, row in enumerate(reader):
            for col_num, cell_value in enumerate(row):
                if cell_value == target_value:
                    coordinates.append((row_num+1, col_num+1))
    return coordinates