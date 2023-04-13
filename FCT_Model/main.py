#! /usr/bin/env python3

""" repast4py implementation of the CASCADE MBSSM Tutorial FCT_Model
"""
# For return type typehints, which for 3.7+ allows class methods to return the named class
from __future__ import annotations
from typing import Dict, Tuple, List

# For virtual classes / methods
from abc import abstractmethod, ABCMeta
import time
from mpi4py import MPI
from repast4py import parameters
import repast4py
import sys
import colorama
from colorama import Fore, Back, Style

import emojis

from alive_progress import alive_bar

import FCT_Model

import SocialNetwork as sn

def main():
    # Command line argument parsing
    parser = repast4py.parameters.create_args_parser()
    args = parser.parse_args()
    params = repast4py.parameters.init_params(args.parameters_file, args.parameters)

    print(Style.RESET_ALL)

    # If multiple MPI ranks have been used, terminate with an error message
    if (MPI.COMM_WORLD.Get_size() > 1):
        if MPI.COMM_WORLD.Get_rank() == 0:
            print(f"Error: This tutorial only supports use of a single MPI rank ({MPI.COMM_WORLD.Get_size()} requested).", file=sys.stderr)
        sys.exit(1)

    
    # Construct the FCT Model
    
    model = FCT_Model.FCT_Model(MPI.COMM_WORLD, params)# 
    print(emojis.encode(colorama.Fore.MAGENTA+"Model Object Created! :smile: \n"))
    print(Style.RESET_ALL)

    #############################################
    # Initialise Agents
    with alive_bar(params.get("count.of.agents"), title="Initialising Agents", bar='circles') as bar:
        for agent in model.init_agents():
            time.sleep(0.0005)
            bar()
    
    print(emojis.encode(colorama.Fore.MAGENTA+"Agent Initialisation Complete! :smile: \n"))
    time.sleep(1)
    print(Style.RESET_ALL)

    
    #############################################
    # Initialise Network
    with alive_bar(params.get("count.of.agents"), title="Creating Agent Network", bar='brackets') as bar:
        for agent in model.init_network():
            time.sleep(0.0005)
            bar()
    print(emojis.encode(colorama.Fore.MAGENTA+"Agent Network Generated! :smile: \n"))
    time.sleep(1)
    print(Style.RESET_ALL)

    #############################################
    # Link Theory
    with alive_bar(params.get("count.of.agents"), title="Linking Agents With Theory", bar='notes') as bar:
        for agent in model.assign_theory():
            time.sleep(0.0005)
            bar()

    print(emojis.encode(colorama.Fore.MAGENTA+"Agent Network Linked With Theory! :smile: \n"))
    time.sleep(1)
    print(Style.RESET_ALL)


    exit()

    
    

    # Initialise the Schedule
    model.init_schedule()

    # Run the model
    print(Fore.LIGHTCYAN_EX + "Running Model")
    time.sleep(1)
    
    with alive_bar(params.get("stop.at"), title="Running Model", bar='filling') as bar:
        for tick in model.run():
            year = tick // 52
            month = tick % 52
            if tick and tick % 52 == 0:
                print("Year: ", year)
                print("Month: ", month)
                print("Week: ", tick)
            bar()
    model.run()
    


# If this file is launched, run the model. 
if __name__ == "__main__":
    main()
    print("Model run complete")
    exit()
