from __future__ import annotations
from typing import Dict, Tuple, List
import sys
from numpy import random
import numpy as np
from numpy import random
from pyprobs import Probability as pr
from repast4py import space
import repast4py
from FCT_Agent import FCT_Agent
from mpi4py import MPI
import os,binascii
from core.StructuralEntity import StructuralEntity
from core.Communicator import Communicator

class FCT_Communicator(StructuralEntity, Communicator):
    
    def __init__(self, context, reach: int):
        self.reach = reach
        self.context = context
        self.total_events_list = []
        self.total_event_number = 0

        def rand_binary(p):# function to return binary string
        # Variable to store the
        # string
            key1 = ""
        
            # Loop to find the string
            # of desired length
            for i in range(p):
                
                # randint function to generate
                # 0, 1 randomly and converting
                # the result into str
                temp = str(random.randint(0, 1))
        
                # Concatenation the random 0, 1
                # to the final result
                key1 += temp
                
            return(key1)
        
        def rand_hex(p):
            return binascii.b2a_hex(os.urandom(p))
        
        def communicate_event(type):
            event_list = self.total_events_list
            match type:
                case "binary":
                    event = rand_binary(16)
                case "hex":
                    event = rand_hex(16)
                case _:
                    print("Invalid event type")
                    raise Exception("Invalid event type inputted to communicator object")