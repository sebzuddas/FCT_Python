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

    # Construct the Segregation Model
    model = FCT_Model.FCT_Model(MPI.COMM_WORLD, params)

    # Initialise Agents
    model.init_agents()

    # Initialise the Schedule
    model.init_schedule()

    # Run the model
    model.run()


# If this file is launched, run the model. 
if __name__ == "__main__":
    main()
