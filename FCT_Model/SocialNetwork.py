"""
This section of code shall be used to implement the social element of the model, ie the SocialNetwork class.
The code is adapted from the 'rumor' example program https://repast.github.io/repast4py.site/guide/user_guide.html#_tutorial_2_the_rumor_network_model

"""

import networkx as nx

from typing import Dict
from mpi4py import MPI
import numpy as np
import json


import csv

from repast4py.network import write_network, read_network
from repast4py import context as ctx
from repast4py import core, random, schedule, logging, parameters



def main():
    """The main function for the SocialNetwork model.

    This function is called by repast4py when the model is run.
    """


    # Initialise the parameters
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(args.parameters_file, args.parameters)


    # Get the parameters from the parameter file
    n_agents = params.get('count.of.agents')

    # Generate the network file if it doesn't exist
    fname = "FCT_Model/props/network/FCT_network.txt"
    generate_network_file(fname, 1, n_agents)


def generate_network_file(fname: str, n_ranks: int, n_agents: int):
    """Generates a network file using repast4py.network.write_network.

    Args:
        fname: the name of the file to write to
        n_ranks: the number of process ranks to distribute the file over
        n_agents: the number of agents (node) in the network
    """

    g = nx.connected_watts_strogatz_graph(n_agents, 2, 0.25)

    fname = "FCT_Model/props/network/connected_watts_strogatz_graph.txt"
    try:
        import nxmetis
        write_network(g, 'FCT_network', fname, n_ranks, partition_method='metis')
    except ImportError:
        write_network(g, 'FCT_network', fname, n_ranks)




##### Generating Areas for the DQ model #####

def create_areas(width, height):
    area_1 = ((0, 0), (width // 2, height // 2))
    area_2 = ((0, height // 2), (width // 2, height))
    area_3 = ((width // 4, height // 4), (3 * width // 4, 3 * height // 4))
    area_4 = ((width // 2, 0), (width, height // 2))
    area_5 = ((width // 2, height // 2), (width, height))
    
    return [area_1, area_2, area_3, area_4, area_5]

def is_inside_area(x, y, area):
    (x_min, y_min), (x_max, y_max) = area
    return x_min <= x < x_max and y_min <= y < y_max

def generate_DQ_areas(filename, width, height):
    areas = create_areas(width, height)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        for y in range(height):
            row = []
            for x in range(width):
                for i, area in enumerate(areas, start=1):
                    if is_inside_area(x, y, area):
                        row.append(i)
                        break
            writer.writerow(row)

##### Generating Agents for the network #####

def generate_agent_json_file(num_agents, filename, attributes: Dict[str, list]):
    
    agent_data = []
    agent_age_lowest = attributes["age"][0]
    agent_age_highest = attributes["age"][1]
    agent_drinking_lowest = attributes["drinking_status"][0]
    agent_drinking_highest = attributes["drinking_status"][1]

    #def __init__(self, id:int, rank:int, deprivation_quintile:int, agent_type:int, threshold:float, sex: bool, age: int, drinking_status: int,  space):

    for i in range(num_agents):
        ##### random numbers #####
        sex_rand = int(random.default_rng.choice([0, 1], p=[0.5, 0.5]))
        age_rand = int(random.default_rng.integers(agent_age_lowest, agent_age_highest))
        agent_drinking_status = int(random.default_rng.integers(agent_drinking_lowest, agent_drinking_highest))
        deprivation_quintile_rand = int(random.default_rng.integers(1, 5))# has to stay constant

        agent = {
            "agent_id": i,
            "agent_type": 0, # all agents are the same type "FCT_agent"
            "rank": 0,# agents are all in the same rank
            "deprivation_quintile": deprivation_quintile_rand,
            "sex": sex_rand,
            "age": age_rand,
            "drinking_status": agent_drinking_status,
        }

        agent_data.append(agent)

    with open(filename, 'w') as outfile:
        json.dump(agent_data, outfile, indent=4)
    
    with open(filename, 'r') as infile: 
        agent_data = json.load(infile)

    updated_lines = []
    with open('FCT_Model/props/network/connected_watts_strogatz_graph.txt', 'r') as network_file:
        lines = network_file.readlines()
        for line in lines:

            if line.startswith('FCT_network'):# at the start of the file 
                updated_lines.append(line)
                mode = 0# make amendments to the agents
                continue# skip the line
            elif line.startswith('EDGES'):
                mode = 1
                updated_lines.append(line)
                continue
                
            if mode == 0:
                agent_id = int(line.split()[0])    
                agent_info = next((agent for agent in agent_data if agent['agent_id'] == agent_id), None)

                if agent_info is not None:
                    # Create a new dictionary without the first three elements
                    keys_to_remove = list(agent_info.keys())[:3]
                    updated_agent_info = {key: agent_info[key] for key in agent_info if key not in keys_to_remove}

                    # Convert the dictionary back to a JSON string
                    updated_agent_info_str = json.dumps(updated_agent_info)

                    line = line.strip() + ' ' + updated_agent_info_str + '\n'

                updated_lines.append(line)
            elif mode==1:
                updated_lines.append(line)

    # Write updated lines to a new file
    with open('FCT_Model/props/network/connected_watts_strogatz_graph_updated.txt', 'w') as updated_network_file:
        updated_network_file.writelines(updated_lines)

def generate_agent_distributions(type):

    dict = {"age": [], "drinking_status": []}


    experiment = type
    match experiment:
       
        case 1:# normal population, low drinking status
            dict["age"] = [18, 80]
            dict["drinking_status"] = [0, 2]
            return dict
        
        case 2:# normal population, high drinking status
            dict["age"] = [18, 80]
            dict["drinking_status"] = [2, 5]
            return dict
                
        case 3:# low population, high drinking status
            dict["age"] = [18, 40]
            dict["drinking_status"] = [2, 5]
            return dict
        
        case 4:# low population, normal drinking status
            dict["age"] = [18, 40]
            dict["drinking_status"] = [0, 5]
            return dict
            
        case 5:# low population, low drinking status
            dict["age"] = [18, 40]
            dict["drinking_status"] = [0, 2]
            return dict
        
        case 6:# high population, high drinking status
            dict["age"] = [40, 80]
            dict["drinking_status"] = [2, 5]
            return dict
        case 7:# high population, normal drinking status
            dict["age"] = [40, 80]
            dict["drinking_status"] = [0, 5]
            return dict
            
        case 8:# high population, low drinking status
            dict["age"] = [40, 40]
            dict["drinking_status"] = [0, 2]
            return dict

        case _:# normal population, normal drinking status
            dict["age"] = [18, 80]
            dict["drinking_status"] = [0, 5]
            return dict

if __name__ == "__main__":
    main()