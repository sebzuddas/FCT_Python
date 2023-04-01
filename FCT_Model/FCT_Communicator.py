from __future__ import annotations
from typing import Dict, Tuple, List
import sys
from numpy import random
import random
from pyprobs import Probability as pr
from repast4py import space
import repast4py
from FCT_Agent import FCT_Agent
from mpi4py import MPI
import os,binascii
from core.Communicator import Communicator

class FCT_Communicator(Communicator):

    def __init__(self, context, discrete_space, reach: int):
        self.reach = reach
        self.context = context
        self.discrete_space = discrete_space
        self.total_event_list = {}
        self.total_event_number = 0

    def rand_binary(self, length):
        return ''.join(str(random.randint(0, 1)) for _ in range(length))

    def rand_hex(self, p):
        return binascii.b2a_hex(os.urandom(p))
    
    def generate_event(self, type:str):
        match type:
            case "b":
                event = self.rand_binary(16)
                self.total_event_number += 1
                self.total_event_list[self.total_event_number] = event
                event_and_number = (event, self.total_event_number)
                return event_and_number
            
            case "h":
                event = self.rand_hex(16)
                self.total_event_number += 1
                self.total_event_list[self.total_event_number] = event
                event_and_number = (event, self.total_event_number)
                return event_and_number
            
            case _:
                print("Invalid event type")
                raise Exception("Invalid event type inputted to communicator object")
            
    ###############################
    # Getters
    def get_event_list(self):
        return self.total_event_list
    ###############################
    # Setters