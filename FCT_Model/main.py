#! /usr/bin/env python3

""" repast4py implementation of the CASCADE MBSSM Tutorial FCT_Model
"""
# For return type typehints, which for 3.7+ allows class methods to return the named class
from __future__ import annotations
from typing import Dict, Tuple, List

# For virtual classes / methods
from abc import abstractmethod, ABCMeta

from mpi4py import MPI
from repast4py import parameters
import repast4py
import sys

import FCT_Model

import SocialNetwork as sn

def main():
    # Command line argument parsing
    parser = repast4py.parameters.create_args_parser()
    args = parser.parse_args()
    params = repast4py.parameters.init_params(args.parameters_file, args.parameters)


    # If multiple MPI ranks have been used, terminate with an error message
    if (MPI.COMM_WORLD.Get_size() > 1):
        if MPI.COMM_WORLD.Get_rank() == 0:
            print(f"Error: This tutorial only supports use of a single MPI rank ({MPI.COMM_WORLD.Get_size()} requested).", file=sys.stderr)
        sys.exit(1)
    
    # Construct the FCT Model
    
    model = FCT_Model.FCT_Model(MPI.COMM_WORLD, params)# 

    sn.generate_network_file("FCT_Model/props/network/FCT_network.txt", MPI.COMM_WORLD.size, params.get('count.of.agents'))

    #sn.generate_DQ_areas(params.get('area.file'), params.get('board.size'), params.get('board.size'))
    #sn.test_fcn()
    # Initialise Agents

    #sn.generate_agent_json_file(params.get("count.of.agents"), params.get("agent.props.file"), sn.generate_agent_distributions(0))

    model.init_agents()

    #TODO network
    #model.init_network()

    #TODO environment
    #model.init_environment()

    #TODO event generator
    #model.init_event_generator()

    # Initialise the Schedule
    model.init_schedule()

    # Run the model
    model.run()
    print("Model run complete")
    exit()


# If this file is launched, run the model. 
if __name__ == "__main__":
    main()
