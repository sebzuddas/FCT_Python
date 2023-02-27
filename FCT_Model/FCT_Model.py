from __future__ import annotations
from typing import Dict, Tuple, List
import pathlib
from dataclasses import dataclass

from repast4py import context, schedule, random, logging
import repast4py

from core.Model import Model

from Board import Board
from FCT_Agent import FCT_Agent
from FundamentalCauseTheory import FundamentalCauseTheory
from SocialTheoriesMediator import SocialTheoriesMediator


# # Reduce-type Logging Only!
# @dataclass
# class IndividualAgentInfo:
#     strategy_multiplier: int = 0
#     deprivation_quintile: int = 0




class FCT_Model(Model):

    def __init__(self, comm, params: Dict):
        self.__comm = comm
        # TODO: Define the context for agents
        self.__context:repast4py.context.SharedContext = repast4py.context.SharedContext(comm)

        self.__rank:int = self.__comm.Get_rank()

        # Model parameters that initialise the model 
        self.__props = params
        self.__stop_at:int = self.__props["stop.at"] if "stop.at" in params else 0
        self.__count_of_agents:int = self.__props["count.of.agents"] if "count.of.agents" in params else 0
        self.__board_size:int = self.__props["board.size"] if "board.size" in params else 0
        self.__threshold:float = self.__props["threshold"] if "threshold" in params else 0
        
        
        #Added params
        self.__min_age: int = self.__props["min.age"] if "min.age" in params else 0
        self.__max_age: int = self.__props["max.age"] if "max.age" in params else 0
        self.__random_seed:int = self.__props["random.seed"] if "random.seed" in params else 0


        repast4py.random.init(rng_seed=self.__random_seed)# initialise pseudo-random number generator with the random seed from the props
        
        
        """
        #TODO Include other model parameters including 
            #TODO Distribution of agents that are wealthy
            #TODO Distribution of agents that are well connected 
                #TODO Then make this influence social network
            #TODO Distribution of agents that are well educated
            #TODO Distribution of agents that are have a strong social infuence
                #TODO How to include this in the network?
            #TODO Distribution of agents that have easy access to healthcare
        """
    	# Validate that the board size contains at least one more cell than the count of agents, so that movement can occur.
        if self.__count_of_agents >= (self.__board_size * self.__board_size):
            raise Exception(f"Invalid Configuration: count.of.agents ({self.__count_of_agents}) must be less than board.size * board.size ({self.__board_size * self.__board_size})")

        

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

        ############
        #OUTPUTS
        #TODO: include tabular logging
        #TODO: include reduce-type logging
        #TODO: look into the given logging method
        
        # initialize the logging
        ## Tabular Logging
        self.agent_logger = logging.TabularLogger(comm, params['tabular.logger'], ['tick', 'agent_id', 'sex', 'age'])
        self.log_agents()
        ## Reduce-type Logging
        # self.individual_agent_info = IndividualAgentInfo()
        # loggers = logging.create_loggers(self.__, op=MPI.SUM, names={'total_meets': 'total'}, rank=rank)
        # loggers += logging.create_loggers(self.meet_log, op=MPI.MIN, names={'min_meets': 'min'}, rank=rank)
        # loggers += logging.create_loggers(self.meet_log, op=MPI.MAX, names={'max_meets': 'max'}, rank=rank)
        # self.data_set = logging.ReducingDataSet(loggers, MPI.COMM_WORLD, params['meet_log_file'])


        ###########
        #Predefined output method - records the parameters at the beginning of each run
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

        #TODO: Reduce-type logging
        # # count the initial colocations at time 0 and log
        # for agent in self.__context.agents():
        #     agent.count_colocations(self.grid, self.meet_log)
        # self.data_set.log(0)
        # self.meet_log.max_meets = self.meet_log.min_meets = self.meet_log.total_meets = 0
        # self.log_agents()

    def do_situational_mechanisms(self):
        for agent in self.__context.agents(FCT_Agent.TYPE, count=self.__count_of_agents, shuffle=True):
            # TODO: call doSituation for each agent
            agent.do_situation()
    
    def do_action_mechanisms(self):
        for agent in self.__context.agents(FCT_Agent.TYPE, count=self.__count_of_agents, shuffle=True):
            # TODO: call doAction for each agent
            agent.do_action()


    def do_transformational_mechanisms(self):
        # TODO: call doTransformation of the Board structural entity
        self.__board.do_transformation()
    
    #TODO: define a function to perform actions every tick
    #TODO: Make sure that the do_per_tick function works on a per week basis. 
    def do_per_tick(self):# do these things every week. 
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
            if current_tick == self.__stop_at:#or self.__board.get_avg_satisfaction() == 1
                self.__board.print_board_to_screen()
            
            # stop when all agents are satisfied
            # if self.__board.get_avg_satisfaction() == 1:
            #     self._runner.stop()
    
    def do_per_month(self):
        print('Do this per month')

    def do_per_year(self):
        for agent in self.__context.agents(FCT_Agent.TYPE, count=self.__count_of_agents, shuffle=True):
            # age the agents yearly
            agent.age_agent()
            # calculate the probability of death every year
            # agent.calculate_death_probability()
            # agent.calculate_resources()


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

            #############################################################################
            #FCT level parameters
            #Create a random integer between 1 and 5 to put agents in the deprivation quintile
            #TODO see if theres a way to put this in a distribution
            #TODO see if theres a way to include params
            deprivation_quintile_rand = repast4py.random.default_rng.integers(1, 5)

            #Create a random float between *FIND BOUNDS* to determine agent drinking behaviour
            #TODO find numbers from jens model
            mean_weekly_units_rand = float(repast4py.random.default_rng.integers(0, 1300)/10)

            #Create a random integer between 1-3 to represent :
            #1. low education (maybe they can decode 33% of the time)
            #2. medium education (decode 66% of the time)
            #3. high education (decode 99% of the time)
            # levels among the agent population. 
            education_rand = repast4py.random.default_rng.integers(1, 3)

            #Create a random integer between 1-5 to represent personal wealth
            personal_wealth_rand = repast4py.random.default_rng.integers(1, 5)

            #############################################################################
            #Agent level parameters

            #Create a random generator for generating men/women
            sex_rand = bool(repast4py.random.default_rng.choice([0, 1], p=[0.5, 0.5]))
            
            #Create a random number generator for assigning age
            #TODO: set appropriate age ranges
            #TODO: get age ranges from props file 
            age_rand = repast4py.random.default_rng.integers(self.__min_age, self.__max_age)
            
            #Create a random generator for drinking status boolean
            drinking_status_rand = bool(repast4py.random.default_rng.integers(0, 1))

            #TODO: understand this section of code
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
            #def __init__(self, id:int, rank:int, agent_type:int, threshold:float, sex: bool, age: int, drinking_status: bool,  space):
            agent = FCT_Agent(i, self.__rank, agent_type, self.__threshold, sex_rand, age_rand, drinking_status_rand, self.__discrete_space)

            # create theory object
            #def __init__(self, context, space, deprivation_quintile: int, mean_weekly_units:float, education:int, personal_wealth:int):
            theory = FundamentalCauseTheory(self.__context,  deprivation_quintile_rand, mean_weekly_units_rand, education_rand, personal_wealth_rand, self.__discrete_space)

            # create mediator object
            mediator = SocialTheoriesMediator([theory])

            # connect the individual agent with its mediator
            agent.set_mediator(mediator)
            mediator.set_agent(agent)

            # Add the agent to the context and discrete space
            self.__context.add(agent)
            self.__discrete_space.move(agent, initial_location)

        # print the initial state of the board
        self.__board.print_board_to_screen()

    def log_agents(self):
        #TODO: get theory level parameters for each agent to be logged. 
        tick = self._runner.schedule.tick
        for agent in self.__context.agents():
            self.agent_logger.log_row(tick, agent.id, agent.sex, agent.age)
        self.agent_logger.write()

    def run(self):
        self._runner.execute()

    def init_schedule(self):
        # schedule actions every week
        self._runner.schedule_repeating_event(1, 1, self.do_per_tick)
        
        # schedule actions every month
        self._runner.schedule_repeating_event(1, 4, self.do_per_month)

        # schedule actions every year
        self._runner.schedule_repeating_event(1, 52, self.do_per_year)

        # schedule stopping condition at max tick
        self._runner.schedule_stop(self.__stop_at)
        
        #Datalogging
        self._runner.schedule_repeating_event(1, 4, self.log_agents)
