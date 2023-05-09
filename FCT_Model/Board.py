from __future__ import annotations
from typing import Dict, Tuple, List
import sys
from numpy import random
import numpy as np
from pyprobs import Probability as pr
from repast4py import space
import repast4py
from FCT_Agent import FCT_Agent
from mpi4py import MPI
from core.StructuralEntity import StructuralEntity

import colorama
import emojis


# This is where the social structures go. Here is where the network is implemented. 
class Board(StructuralEntity):

    def __init__(self, context, discrete_space):
        self.__context = context
        self.__discrete_space = discrete_space
        self.__avg_satisfaction: float = 0.0
        self.__segregation_index: float = 0.0
        self.__deprivation_quiltile: int = 0
        # # self.deprivation_probability_list: float [[0.02, 0.012, 0.01, 0.008, 0.005], [0.013, 0.011, 0.009, 0.008, 0.008],[0.01, 0.009, 0.009, 0.009, 0.007], [0.01, 0.01, 0.009, 0.009, 0.009],[0.007, 0.011, 0.008, 0.01, 0.016]]
        # self.deprivation_probability_list: float [[0.3, 0], [0.3, 0], [0.4, 0], [0, 0.4], [0, 0.6]]


    def __update_deprivation_quintile(self, deprivation_probability_list):
        swap_total = []
        for agent in self.__context.agents(FCT_Agent.TYPE, shuffle=True):

            if pr.prob(deprivation_probability_list[agent.get_deprivation_quintile()][0]) == True:# get agents that can swap and are less than 30
                swap_total.append([agent.get_deprivation_quintile(), agent.id, "UP"])
                
                
            elif pr.prob(deprivation_probability_list[agent.get_deprivation_quintile()][1]) == True:# get agents that can swap and are greater than 30
                swap_total.append([agent.get_deprivation_quintile(), agent.id, "DOWN"])

            else:
                pass

        #sort swap array by object rank
        #swap_total = [x for x in swap_total if isinstance(x, list)]# remove 0s 
        #swap_total = sorted(swap_total, key=lambda x: x[0])# sort by dq

        swap_up = [x for x in swap_total if x[2] == "UP"]
        swap_down = [x for x in swap_total if x[2] == "DOWN"]
        # print(swap_up)
        # print(swap_down)
        # print(len(swap_up), len(swap_down))

        if len(swap_up) > len(swap_down):
            # Repeat the last element in swap_down until the lengths match
            swap_down += [swap_down[-1]] * (len(swap_up) - len(swap_down))

        # Pair up swap_up with swap_down
        swap_pairs = list(zip(swap_up, swap_down))

        #swap the pairs ensuring that the two 
        #print one element of swap_pairs
        #print(swap_pairs)
        #print(len(swap_pairs))

        for i in range(len(swap_pairs)):

            agent_1_id = swap_pairs[i][0][1]
            agent_2_id = swap_pairs[i][1][1]

            agent_1_dq = swap_pairs[i][0][0]
            agent_2_dq = swap_pairs[i][1][0]

            # print('swap pair: ', agent_1_id, agent_2_id)
            # print(swap_pairs)

            for agent in self.__context.agents(FCT_Agent.TYPE):
                if agent.id == agent_1_id:
                    #print('agent1ID: ', agent.id,' currentDQ: ', agent.get_deprivation_quintile(),' subsequentDQ: ', agent_2_dq)
                    agent.set_deprivation_quintile(agent_2_dq)

            for agent in self.__context.agents(FCT_Agent.TYPE):
                if agent.id == agent_2_id:
                    #print('agent2ID: ', agent.id,' currentDQ: ', agent.get_deprivation_quintile(),' subsequentDQ: ', agent_1_dq)
                    agent.set_deprivation_quintile(agent_1_dq)

    def update_social_network(self):
        #TODO implement social network updating procedure. 
        pass

    def call_transformation(self):
        self.__update_deprivation_quintile(deprivation_probability_list=[[0.3, 0], [0.3, 0], [0.4, 0], [0, 0.4], [0, 0.6]])

    def get_avg_satisfaction(self) -> float:
        return self.__avg_satisfaction

    def get_segregation_index(self) -> float:
        return self.__segregation_index

    def print_board_to_screen(self):
        local_bounds = self.__discrete_space.get_local_bounds()
        board_origin_x = local_bounds.xmin
        board_origin_y = local_bounds.ymin
        board_size_x = local_bounds.xextent
        board_size_y = local_bounds.yextent
        print("-" * (board_size_x + 2))
        for y in range(board_origin_y, board_origin_y + board_size_y):
            row = "|"
            for x in range(board_origin_x, board_origin_x + board_size_x):
                point = repast4py.space.DiscretePoint(x, y)
                agent_count_at_point = self.__discrete_space.get_num_agents(point)

                # Print a warning/error to stderr if there is more than 1 agent at a given location
                if agent_count_at_point > 1:
                    print(f"Number of agents at {x}, {y}: {agent_count_at_point}", file=sys.stderr)
                # If there are no agents, output an empty space
                if agent_count_at_point == 0:
                    row += "_"
                else: 
                    # If there is an agent, get the first agent at the location
                    agent = self.__discrete_space.get_agent(point)
                    # Add the appropriate character to the string row
                    match agent.get_deprivation_quintile():
                        case 0:
                            row += emojis.encode(":one:")

                        case 1:
                            row += emojis.encode(":two:")

                        case 2:
                            row += emojis.encode(":three:")

                        case 3:
                            row += emojis.encode(":four:")
                        
                        case 4:
                            row += emojis.encode(":five:")
                    

            row += "|"
            print(row)
        print("-" * (board_size_x + 2))

