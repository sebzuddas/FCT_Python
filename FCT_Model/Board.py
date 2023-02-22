from __future__ import annotations
from typing import Dict, Tuple, List
import sys

from repast4py import space
import repast4py
from FCT_Agent import FCT_Agent

from core.StructuralEntity import StructuralEntity

# TODO: inherit StructuralEntity
class Board(StructuralEntity):

    def __init__(self, context, discrete_space):
        self.__context = context
        self.__discrete_space = discrete_space

	    # TODO: define 2 variables for satisfaction and segregation index
        self.__avg_satisfaction: float = 0.0
        self.__segregation_index: float = 0.0

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
                    if agent.get_agent_type() == 0:
                        count_type0 += 1
                    elif agent.get_agent_type() == 1:
                        count_type1 += 1

        # sweep areas (defined by window size)
        segregationIndex = 0.0
        while True:
            # determine window coordinates: (x0,y0) to (x1,y1)
            x1 = x0 + window_size - 1;
            y1 = y0 + window_size - 1;

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
                        if agent.get_agent_type() == 0:
                            local_count_type0 += 1
                        elif agent.get_agent_type() == 1:
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

    # TODO: override do_transformation();
    def do_transformation(self):
        # TODO: transformational mechanisms: update avg satisfaction and segregation index
        self.__update_avg_satisfaction()
        self.__update_segregation_index()

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
                    row += " "
                else: 
                    # If there is an agent, get the first agent at the location
                    agent = self.__discrete_space.get_agent(point)
                    # Add the appropriate character to the string row
                    if agent.get_agent_type() == 0:
                        row += "X"
                    elif agent.get_agent_type() == 1:
                        row += "O"
            row += "|"
            print(row)
        print("-" * (board_size_x + 2))

