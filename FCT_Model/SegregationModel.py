from __future__ import annotations
from typing import Dict, Tuple, List
import pathlib

from repast4py import context, schedule
import repast4py

from core.Model import Model

from Board import Board
from SegregationAgent import SegregationAgent
from SchellingTheory import SchellingTheory
from SegregationTheoriesMediator import SegregationTheoriesMediator

class SegregationModel(Model):

    def __init__(self, comm, params: Dict):
        self.__comm = comm
        # TODO: Define the context for agents
        self.__context:repast4py.context.SharedContext = repast4py.context.SharedContext(comm)

        self.__rank:int = self.__comm.Get_rank()

        # Model parameters
        self.__props = params
        self.__stop_at:int = self.__props["stop.at"] if "stop.at" in params else 0
        self.__count_of_agents:int = self.__props["count.of.agents"] if "count.of.agents" in params else 0
        self.__board_size:int = self.__props["board.size"] if "board.size" in params else 0
        self.__threshold:float = self.__props["threshold"] if "threshold" in params else 0

    	# Validate that the board size contains at least one more cell than the count of agents, so that movement can occur.
        if self.__count_of_agents >= (self.__board_size * self.__board_size):
            raise Exception(f"Invalid Configuration: count.of.agents ({self.__count_of_agents}) must be less than board.size * board.size ({self.__board_size * self.__board_size})")

        if self.__rank == 0:
            # Repast4py does not include a clear repast::properties::writeToSVFile, so this code block is equivalent
            output_record_csv_path = pathlib.Path("outputs/record.csv")
            csv_row = ",".join([str(self.__props[key]) for key in sorted(self.__props.keys())]) + "\n"
            if output_record_csv_path.exists():
                if output_record_csv_path.is_file():
                    # Append a single line to the CSV. This can lead to a mismatching number of elements, but matches writeToSVFile
                    with open(output_record_csv_path, "a") as record_csv:
                        record_csv.write(csv_row)
                else:
                    raise Exception(f"{output_record_csv_path} exists but is not a writable file.")
            else:
                # Ensure the destination directory exists
                output_record_csv_path.parent.mkdir(parents=True, exist_ok=True)
                header_row = ",".join(sorted(self.__props.keys())) + "\n"
                # File does not exist, output it to disk with a header row
                with open(output_record_csv_path, "w") as record_csv:
                    record_csv.write(header_row)
                    record_csv.write(csv_row)

        origin:repast4py.space.DiscretePoint = repast4py.space.DiscretePoint(1,1)
        extent:repast4py.space.DiscretePoint = repast4py.space.DiscretePoint(self.__board_size, self.__board_size)

        box = repast4py.space.BoundingBox(origin.x, extent.x, origin.y, extent.y)

        # Define the discrete space
        self.__discrete_space = repast4py.space.SharedGrid(
            'AgentDiscreteSpace', 
            bounds=box, 
            borders=repast4py.space.BorderType.Sticky, 
            occupancy=repast4py.space.OccupancyType.Multiple, 
            buffer_size=2, 
            comm=self.__comm)

        # Output the Rank, and Bounds to match RepastHPC
        local_bounds = self.__discrete_space.get_local_bounds()
        print(f"RANK {self.__rank} BOUNDS Point[{local_bounds.xmin}, {local_bounds.ymin}] Point[{local_bounds.xextent}, {local_bounds.yextent}]")
        self.__context.add_projection(self.__discrete_space)

        # Define the board
        # TODO: init at the macro level: the Board structural entity
        self.__board:Board = Board(self.__context, self.__discrete_space)

        # Repast4py lacks some of the singletons available in repastHPC, so the runner is a member of the Model class.
        self._runner: repast4py.schedule.SharedScheduleRunner = repast4py.schedule.init_schedule_runner(self.__comm)

    def do_situational_mechanisms(self):
        for agent in self.__context.agents(SegregationAgent.TYPE, count=self.__count_of_agents, shuffle=True):
            # TODO: call doSituation for each agent
            agent.do_situation()
    
    def do_action_mechanisms(self):
        for agent in self.__context.agents(SegregationAgent.TYPE, count=self.__count_of_agents, shuffle=True):
            # TODO: call doAction for each agent
            agent.do_action()

    def do_transformational_mechanisms(self):
        # TODO: call doTransformation of the Board structural entity
        self.__board.do_transformation()
    
    # TODO: define a function to perform actions every tick
    def do_per_tick(self):
        # TODO: call three mechanisms in the correct order
        self.do_situational_mechanisms()
        self.do_action_mechanisms()
        self.do_transformational_mechanisms()

        # print to screen: satisfaction (every tick) & board (at start and end)
        current_tick = self._runner.schedule.tick
        # Only a single rank outputs the board
        if self.__rank == 0:
            print(f"Tick: {current_tick:.1f}\tSatisfaction: {self.__board.get_avg_satisfaction():.3f}\tSegregation index: {self.__board.get_segregation_index():.3f}")
		
            # print board at the end (tick=mStopAt) or when all agents are satisfied (100% satisfaction)
            if current_tick == self.__stop_at or self.__board.get_avg_satisfaction() == 1:
                self.__board.print_board_to_screen()
            
            # stop when all agents are satisfied
            if self.__board.get_avg_satisfaction() == 1:
                self._runner.stop()
    
    def init_agents(self):
        count_type_0:int = int(self.__count_of_agents // 2) # // for integer/floor division
        count_type_1:int = int(self.__count_of_agents  - count_type_0)
        
        local_bounds = self.__discrete_space.get_local_bounds()

        for i in range(self.__count_of_agents):
            # Agent start with a random location
            
            # Note: repast's default_rng (i.e. numpy) rng integers is [low, high), i.e. high is exclusive 
            x_rand = repast4py.random.default_rng.integers(local_bounds.xmin, local_bounds.xmin + local_bounds.xextent)
            y_rand = repast4py.random.default_rng.integers(local_bounds.ymin, local_bounds.ymin + local_bounds.yextent)
            initial_location = repast4py.space.DiscretePoint(x_rand, y_rand)
            # Generate new positions until the number of agents at that position is 0. 
            while self.__discrete_space.get_num_agents(initial_location) != 0: 
                x_rand = repast4py.random.default_rng.integers(local_bounds.xmin, local_bounds.xmin + local_bounds.xextent)
                y_rand = repast4py.random.default_rng.integers(local_bounds.ymin, local_bounds.ymin + local_bounds.yextent)
                initial_location = repast4py.space.DiscretePoint(x_rand, y_rand)

            # assign the first N agents to type 0 then the rest to type 1
            # agent_id = (i, self.__rank, 0)
            # This is the agents type / group in the schelling model, not the repast4py Agent.type 
            agent_type = 0
            if count_type_0 > 0:
                agent_type = 0
                count_type_0 -= 1
            else:
                agent_type = 1
                count_type_1 -= 1

            # TODO: init at the micro level: agent, theory, theory mediator
            # create agent object
            agent = SegregationAgent(i, self.__rank, agent_type, self.__threshold, self.__discrete_space)

            # create theory object
            theory = SchellingTheory(self.__context, self.__discrete_space)

            # create mediator object
            mediator = SegregationTheoriesMediator([theory])

            # connect agent with the mediator
            agent.set_mediator(mediator)
            mediator.set_agent(agent)

            # Add the agent to the context and discrete space
            self.__context.add(agent)
            self.__discrete_space.move(agent, initial_location)

        # print the initial state of the board
        self.__board.print_board_to_screen()     

    def run(self):
        self._runner.execute()

    # TODO: define a function to init schedulers
    def init_schedule(self):
        # TODO: schedule actions every tick
        self._runner.schedule_repeating_event(1, 1, self.do_per_tick)
        # TODO: schedule stopping condition at max tick
        self._runner.schedule_stop(self.__stop_at)
