from __future__ import annotations
from typing import Dict, Tuple, List
from abc import abstractmethod, ABCMeta

class Communicator(metaclass=ABCMeta):
#    The communicator is used to generate events for agents to decode. 
#    The reach of the communicator is the number of agents that the communicator sends events to. 

    def __init__(self, context, reach: int):
        self.context = context
        self.current_event = None # stores the current event
        self.total_events_list = [] # stores all the events that have been sent out
        self.reach = reach # the number of agents that the communicator can communicate to for any tick

        pass

    # update the adjustment level variable (private).
	# Modeller should write getter function(s) to access to adjustment level variable, depending on the data structure (it can be a value or array)
    @abstractmethod
    def generate_event(self):
        pass




