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

	    # TODO: define 2 variables for satisfaction and segregation index
        self.__avg_satisfaction: float = 0.0
        self.__segregation_index: float = 0.0
        self.__deprivation_quiltile: int = 0
        self.__deprivation_move_up_probability: float = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.__deprivation_move_down_probability: float = [0.0, 0.0, 0.0, 0.0, 0.0]
        # self.deprivation_probability_list: float [[0.02, 0.012, 0.01, 0.008, 0.005], [0.013, 0.011, 0.009, 0.008, 0.008],[0.01, 0.009, 0.009, 0.009, 0.007], [0.01, 0.01, 0.009, 0.009, 0.009],[0.007, 0.011, 0.008, 0.01, 0.016]]
        # self.deprivation_probability_list: float [[0.3, 0], [0.3, 0], [0.4, 0], [0, 0.4], [0, 0.6]]
        


    def __update_avg_satisfaction(self):
        avg_satisfaction = 0.0
        count = 0
        # Must use a try-except block in the requested type id has never been present in the context, which throws
        try:
            count = self.__context.size([FCT_Agent.TYPE])[FCT_Agent.TYPE]
        except KeyError:
            # repast4py.context.size raises a key error if the requested type is not present
            pass
        
        if count > 0:
            total_satisfaction = 0
            for agent in self.__context.agents(agent_type=FCT_Agent.TYPE):
                total_satisfaction += int(agent.get_satisfied_status())
            avg_satisfaction = total_satisfaction / count
        self.__avg_satisfaction = avg_satisfaction
        
    def __update_segregation_index(self):

        """Calculate the segregation index / index of dissimilarity, using a window_size of 5. 
        
            D = \frac{1}{2}\sum_{i=1}^{N}\left|\frac{a_i}{A} - \frac{b_i}{B}\right|

            Where:
            - N is the number of areas / windows
            - a_i is the population of group A in area i 
            - A is the total population of group A
            - b_i is the population of group B in area i 
            - B is the total population of group B

            https://en.wikipedia.org/wiki/Index_of_dissimilarity
        """

        x0 = self.__discrete_space.get_local_bounds().xmin
        y0 = self.__discrete_space.get_local_bounds().ymin
        max_x = x0 + self.__discrete_space.get_local_bounds().xextent - 1 
        max_y = y0 + self.__discrete_space.get_local_bounds().yextent - 1 
        window_size = 5

        count_type0 = 0
        count_type1 = 0

        for x in range(y0, max_x + 1):
            for y in range(x0, max_y + 1):
                point = repast4py.space.DiscretePoint(x, y)
                agent_count_at_point = self.__discrete_space.get_num_agents(point)
                # Print to stderr if there is more than 1 agent at a given coordinatate
                if agent_count_at_point > 1:
                    print("More than 1 agent per cell", file=sys.stderr)
                if agent_count_at_point > 0:
                    # Get the first agent at the location
                    agent = self.__discrete_space.get_agent(point)
                    # Print the appropriate character
                    if agent.get_agent_sex() == 0:
                        count_type0 += 1
                    elif agent.get_agent_sex() == 1:
                        count_type1 += 1

        # sweep areas (defined by window size)
        segregationIndex = 0.0
        while True:
            # determine window coordinates: (x0,y0) to (x1,y1)
            x1 = x0 + window_size - 1
            y1 = y0 + window_size - 1

            # cap if out of range
            if x1 > max_x:
                x1 = max_x
            if y1 > max_y:
                y1 = max_y

            # print(f"Zone coords: ({x0},{y0}) to ({x1},{y1})")

            # find local count by type
            local_count_type0 = 0
            local_count_type1 = 0
            for x in range(y0, x1 + 1):
                for y in range(x0, y1 + 1):
                    point = repast4py.space.DiscretePoint(x, y)
                    agent_count_at_point = self.__discrete_space.get_num_agents(point)
                    # Print to stderr if there is more than 1 agent at a given coordinatate
                    if agent_count_at_point > 1:
                        print("More than 1 agent per cell", file=sys.stderr)
                    if agent_count_at_point > 0:
                        # Get the first agent at the location
                        agent = self.__discrete_space.get_agent(point)
                        # Print the appropriate character
                        if agent.get_agent_sex() == 0:
                            local_count_type0 += 1
                        elif agent.get_agent_sex() == 1:
                            local_count_type1 += 1

            # add to segregation index
            normalised_local_count_type0 = local_count_type0 / count_type0 if count_type0 != 0 else 0
            normalised_local_count_type1 = local_count_type1 / count_type1 if count_type1 != 0 else 0
            segregation_change = abs(normalised_local_count_type1 - normalised_local_count_type0)

            # print(f"Partial segregation: {segregation_change:.5f}")
            segregationIndex += segregation_change

            # exit if the window reaches the max coords
            if x1 == max_x and y1 == max_y:
                break

            # next window coordinates
            x0 = x0 + window_size; #  move along x-axis
            if x0 > max_x: #  when x is out of range
                x0 = self.__discrete_space.get_local_bounds().xmin #  reset x
                y0 = y0 + window_size; # move along y-axis

        self.__segregation_index = segregationIndex / 2.0

    def __update_deprivation_quintile(self, deprivation_probability_list):
        swap_total = []
        #print("number of on rank 0:", self.__context.size("FCT_Agent",0))
        #go through all agents and get their porobability for swapping up or down
        for agent in self.__context.agents(FCT_Agent.TYPE, shuffle=True):
            
            #TODO: why does this return false?

            #print(agent.get_age() <=30 and pr.prob(deprivation_probability_list[agent.get_deprivation_quintile()][0]) == True)
            #print(agent.get_age()<=30)
            #print(agent.get_age() > 30 and pr.prob(deprivation_probability_list[agent.get_deprivation_quintile()][1]) == True)
            #TODO: implement age?

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

    # TODO: override do_transformation();
    def call_transformation(self):
        # TODO: transformational mechanisms: update avg satisfaction and segregation index
        self.__update_avg_satisfaction()
        self.__update_segregation_index()
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
                    print(f"More than 1 agent per cell at {x}, {y}", file=sys.stderr)
                # If there are no agents, output an empty space
                if agent_count_at_point == 0:
                    row += "_"
                else: 
                    # If there is an agent, get the first agent at the location
                    agent = self.__discrete_space.get_agent(point)
                    print(agent)
                    print(agent.get_agent_sex())
                    # Add the appropriate character to the string row
                    if agent.get_agent_sex() == 0:
                        row += emojis.encode(":red_circle:") #Previously X
                    elif agent.get_agent_sex() == 1:
                        row += emojis.encode(":large_blue_circle:") #Previously Y
            row += "|"
            print(row)
        print("-" * (board_size_x + 2))

