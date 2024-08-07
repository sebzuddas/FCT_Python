from __future__ import annotations
from typing import Dict, Tuple, List
import pathlib
from dataclasses import dataclass
import csv
import sys

import json
from repast4py import context, schedule, random, logging
from repast4py.network import write_network, read_network
import repast4py
import re

import numpy as np
from numpy import *

from scipy.special import expit


from alive_progress import alive_bar

import networkx as nx

from core.Model import Model

from Board import Board
from FCT_Agent import FCT_Agent
from FundamentalCauseTheory import FundamentalCauseTheory
from SocialTheoriesMediator import SocialTheoriesMediator
from FCT_Communicator import FCT_Communicator


# # Reduce-type Logging Only!
# @dataclass
# class IndividualAgentInfo:
#     strategy_multiplier: int = 0
#     deprivation_quintile: int = 0

class FCT_Model(Model):

    def __init__(self, comm, params: Dict):
        self.__comm = comm
        self.__context:repast4py.context.SharedContext = repast4py.context.SharedContext(comm)
        self.__rank:int = self.__comm.Get_rank()
        
        
        # Model parameters that initialise the model 
        self.__props = params
        self.__stop_at:int = self.__props["stop.at"] if "stop.at" in params else 0
        self.__count_of_agents:int = self.__props["count.of.agents"] if "count.of.agents" in params else 0
        self.__board_size:int = self.__props["board.size"] if "board.size" in params else 0
        
        
        #Added params
        self.__min_age: int = self.__props["min.age"] if "min.age" in params else 0
        self.__max_age: int = self.__props["max.age"] if "max.age" in params else 0
        self.__random_seed:int = self.__props["random.seed"] if "random.seed" in params else 0

        self.__theory_attributes = None

        repast4py.random.init(rng_seed=self.__random_seed)# initialise pseudo-random number generator with the random seed from the props
        

        self.__network = repast4py.network.DirectedSharedNetwork('fct_network', self.__comm)


        g = nx.connected_watts_strogatz_graph(self.__count_of_agents, 2, 0.25)# generate the network
        fname = "FCT_Model/props/network/graph.txt"
        write_network(g, 'FCT_network', fname, 1)# write the network to a file
        
            
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
        print(f"RANK: {self.__rank} \nBOUNDS: from[{local_bounds.xmin}, {local_bounds.ymin}] to[{local_bounds.xextent}, {local_bounds.yextent}]")
        self.__context.add_projection(self.__discrete_space)
        self.__context.add_projection(self.__network)

        # Define the board
        self.__board:Board = Board(self.__context, self.__discrete_space)

        # Define the communicator
        self.__communicator: FCT_Communicator = FCT_Communicator(self.__context, self.__discrete_space, self.__props.get("communicator.max.reach"))

        # Repast4py lacks some of the singletons available in repastHPC, so the runner is a member of the Model class.
        self._runner: repast4py.schedule.SharedScheduleRunner = repast4py.schedule.init_schedule_runner(self.__comm)

        ############
        #OUTPUTS
        print(self.__props.keys())
        print(params["agent.logger"])
        print(params["theory.logger"])

        self.theory_logger = logging.TabularLogger(comm, params['theory.logger'], ['tick', 'id', 'mean_weekly_units', 'education', 'personal_wealth','power', 'prestige', 'social_connections', 'social_influence', 'knowledge', 'total_resources', 'successful_adaptiation', 'unsuccessful_adaptiation'])
        #TODO: pass board array into the tabular logger
        # self.board_logger = logging.TabularLogger(comm, params['board.logger'])
        # self.log_board()

        self.agent_logger = logging.TabularLogger(comm, params['agent.logger'], ['tick', 'agent_id', 'sex', 'age', 'deprivation_quintile', 'death_count','location_x', 'location_y'])
        self.log_agents()
        self.log_theory()
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
            output_record_csv_path = pathlib.Path("FCT_Model/outputs/record.csv")
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
    ############################
    #MBSSM Mechanisms

    def do_situational_mechanisms(self):

        # different_events = self.__props["communicator.different.events"]

        # if different_events:
        #     rng = np.random.default_rng()
        #     event_type = rng.choice([0, 1], p=[1/2, 1/2])
        #     if event_type == 0:
        #         event = self.__communicator.generate_event('h')
        #     elif event_type == 1:
        #         event = self.__communicator.generate_event('b')
        # else:
        # #Events generated based on a probability:
            
        event = self.__communicator.generate_event('b')


        for agent in self.__context.agents(FCT_Agent.TYPE, count=self.__props["communicator.max.reach"], shuffle=True):
            agent.interpret_event(event)

        for agent in self.__context.agents(FCT_Agent.TYPE, count=self.__count_of_agents, shuffle=True):
            agent.call_situation()
        
    def do_action_mechanisms(self):
        
        for agent_a in self.__context.agents(FCT_Agent.TYPE, count=self.__count_of_agents, shuffle=False):
            rng = np.random.default_rng(seed=self.__props["random.seed"])
            # print(f'agent_a ID: {agent_a.get_agent_id()} and agent_b ID: {agent_b.get_agent_id()} are different agents')
            agent_a_id = agent_a.get_agent_id()
            agent_a_connection_array = agent_a.get_target_connections_array()
            agent_a_solved_events = agent_a.get_agent_solved_events()

            agent_b_id = rng.choice(agent_a_connection_array)
            # print(agent_a_connection_array)            
            # print(f'agent a connection array: {agent_a_connection_array}')
            # print(f'agent a solved events: {agent_a_solved_events}')
            # print(f"agent a ID: {agent_a_id} and agent b ID:  {agent_b_id} are connected agents \n")

            agent_b = self.__context.agent((agent_b_id, 1, 0))#Has to be entered in this format, gets agent b object
            agent_b_solved_events = agent_b.get_agent_solved_events()
            # print(f'agent b solved events: {agent_b_solved_events}, agent a solved events: {agent_a_solved_events}')
            # print(agent_b.get_agent_id())
            # print(f"agent_b: {agent_b}, agent_b_id: {agent_b_id}, agent_a_id: {agent_a_id}")
            
            if agent_a_solved_events != []:# only the first agent needs solved events
                
                agent_a_random_event = rng.choice(agent_a_solved_events)
                # print(f'agent a random event: {agent_a_random_event}')

                if agent_b_solved_events == []:
                    pass
                    # print(f"Agent {agent_a_id} has solved event {agent_a_random_event} and agent {agent_b_id} hasnt solved it")

                elif not np.isin(agent_a_random_event, agent_b_solved_events).any():
                    # print(f"Agent {agent_a_id} has solved event {agent_a_random_event} and agent {agent_b_id} hasnt solved it")
                    # print(agent_b_solved_events)

                    st = rng.uniform(0, 1)

                    if st <= self.__props["communication.success"]:
                        agent_b.handle_event(agent_a_random_event, True)
                    else:
                        agent_b.handle_event(agent_a_random_event, False)

                else:
                    pass
            else:
                pass
        
        for agent in self.__context.agents(FCT_Agent.TYPE, count=self.__count_of_agents, shuffle=True):
            agent.call_action()
        
    def do_transformational_mechanisms(self):
        self.__board.call_transformation()

    def run(self):

        self._runner.execute()
  
    ############################
    #Schedules to do per different time rates.
    def do_per_tick(self):# do these things every week. 
        #print(self.__context)

        self.do_situational_mechanisms()
        self.do_action_mechanisms()
        # self.__board.print_board_to_screen()

        # print to screen: satisfaction (every tick) & board (at start and end)
        current_tick = self._runner.schedule.tick
        print(f"Tick: {current_tick} / {self.__props['stop.at']}")
        # Only a single rank outputs the board
        
        if self.__rank == 0:

            # print board at the end (tick=mStopAt) or when all agents are satisfied (100% satisfaction)
            if current_tick == self.__stop_at:#or self.__board.get_avg_satisfaction() == 1
                self.__board.print_board_to_screen()
            
            # stop when all agents are satisfied
            # if self.__board.get_avg_satisfaction() == 1:
            #     self._runner.stop()
        
    def do_per_month(self):
        print('Do this per month')

    def do_per_year(self):
        self.do_transformational_mechanisms()

        #calculate agents risk
        for agent in self.__context.agents(FCT_Agent.TYPE, count=self.__count_of_agents):

            # age the agents yearly
            age = agent.get_agent_age()
            age += 1
            agent.set_agent_age(age)
            failed_attempts = len(agent.unsolved_events)
            successful_attempts = len(agent.solved_events)

            

            if failed_attempts == 0:
                risk = agent.abs_risk * expit((agent.age-45)/9.5)
        
            else:
                ratio = successful_attempts/(successful_attempts+failed_attempts)

                risk = (agent.abs_risk * (1+ratio-0.5)**self.__props['risk.modifier.beta']) * expit((agent.age-45)/9.5)
            # print(risk)

            # print(f'risk: {risk}')
            if(agent.get_agent_age()>95):
                agent.kill()
            elif risk > self.__props['risk.threshold']:#what parameter should be used here?
                agent.kill()
    
    ############################
    #Initialisers
    def init_agents(self):

        generate_agent_json_file(self.__props.get("count.of.agents"), self.__props.get("agent.props.file"),  generate_agent_distributions(0), True, seed_input=self.__random_seed )
        read_network(self.__props["network.file.updated"], self.__context, create_FCT_agent, restore_FCT_agent) 

        for agent in self.__context.agents(count=self.__count_of_agents):
            
            agent.set_space(self.__discrete_space)# place the agent on the discrete space

            dq = agent.get_deprivation_quintile()
            agent.original_dq = dq
            # print(repast4py.network.DirectedSharedNetwork.num_edges(self.__network, agent))
            # print(agent)
            # print(self.__network.num_edges(agent))
            # print(self.__network.num_edges(id))
            

            random_dq_point = get_random_location(self.__props["board.props.file"], dq, self.__random_seed)
            initial_location = repast4py.space.DiscretePoint(random_dq_point[1], random_dq_point[0])
          
            while self.__discrete_space.get_num_agents(initial_location) != 0:
                random_dq_point = get_random_location(self.__props["board.props.file"], dq, self.__random_seed)
                initial_location = repast4py.space.DiscretePoint(random_dq_point[1], random_dq_point[0])
                # print(initial_location, '\n', self.__discrete_space.get_num_agents(initial_location))

            # Move to the new location
            self.__discrete_space.move(agent, initial_location)
            
            yield
        self.__board.print_board_to_screen()

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
        self._runner.schedule_repeating_event(1, 1, self.log_agents)
        self._runner.schedule_repeating_event(1, 1, self.log_theory)
    
    def init_network(self):
        for agent_a in self.__context.agents(count=self.__count_of_agents, shuffle=False):
        
            rng = np.random.default_rng(seed=self.__random_seed)  # create a default Generator instance
            agent_a_connection_array = agent_a.get_target_connections_array()
            agent_a_target_connections = agent_a.get_target_connections()
            
            agent_a_connections = len(agent_a_connection_array)
            iteration_count = 0

            while agent_a_connections < agent_a_target_connections:

                if iteration_count > 100*self.__count_of_agents:#can't find a suitable agent to connect to
                    break

                agent_b_search_count = 0# to count over searched agents
                for agent_b in self.__context.agents(count=self.__count_of_agents, shuffle=True):
                    agent_a_id = agent_a.get_agent_id()
                    agent_b_id = agent_b.get_agent_id()

                    agent_b_target_connections = agent_b.get_target_connections()
                    agent_b_connection_array = agent_b.get_target_connections_array()

                    if agent_b_target_connections == len(agent_a_connection_array): # move onto next agent if the agent is already full
                        break

                    if agent_a == agent_b:# agent can't link to itself
                        break
                    
                    dq_test = rng.integers(0, 100)
                    dq_test_pass = False
                    age_test = rng.integers(0, 100)
                    age_test_pass = False
                    sex_test = rng.integers(0, 100)
                    sex_test_pass = False
                    education_test = rng.integers(0, 100)
                    education_test_pass = False
                    drinking_status_test = rng.integers(0, 100)
                    drinking_status_test_pass = False


                    if agent_b.get_id() not in agent_a_connection_array and len(agent_b_connection_array) < agent_b_target_connections:#check agent b isn't in agent A's connection array
                            
                        if dq_test <= 25:#25% of connections to be made within deprivation quintile
                            if agent_b.get_deprivation_quintile() == agent_a.get_deprivation_quintile():
                                dq_test_pass = True
                            else:
                                pass
                        if age_test <= 82:#82% of connections to be made within age range
                            if agent_a.get_agent_age() - 5 < agent_b.get_agent_age() and agent_b.get_agent_age() < agent_a.get_agent_age()+5:
                                age_test_pass = True
                            else:
                                pass
                        if sex_test <= 5:#5% of connections to be made wrt sex
                                if agent_a.get_agent_sex() == agent_b.get_agent_sex():
                                    sex_test_pass = True
                                else:
                                    pass
                        if education_test <= 75:#75% of connections to be made wrt education
                            if self.__theory_attributes[agent_a_id]["education"] == self.__theory_attributes[agent_b_id]["education"]:
                                education_test_pass = True
                            elif self.__theory_attributes[agent_a_id]["education"] == self.__theory_attributes[agent_b_id]["education"]+1:
                                education_test_pass = True
                            elif self.__theory_attributes[agent_a_id]["education"] == self.__theory_attributes[agent_b_id]["education"]-1:
                                education_test_pass = True
                            else: 
                                pass
                        # if drinking_status_test <= 15:#15% of connections to be made wrt drinking status
                        #     if agent_a.get_agent_drinking_status() == agent_b.get_agent_drinking_status():
                        #         drinking_status_test_pass = True
                        #     elif agent_a.get_agent_drinking_status()-1 == agent_b.get_agent_drinking_status():
                        #         drinking_status_test_pass = True
                        #     elif agent_a.get_agent_drinking_status()+1 == agent_b.get_agent_drinking_status():
                        #         drinking_status_test_pass = True
                        #     else:
                        #         pass
                        # if dq_test_pass == age_test_pass == sex_test_pass == education_test_pass == drinking_status_test_pass == True:#TODO: amend
                        if dq_test_pass and age_test_pass or sex_test_pass and drinking_status_test_pass == True:#TODO: amend
                            # print(iteration_count)
                            agent_b.append_connections_array(agent_a.get_id())#####SORT OUT THIS CONNECTIONS ARRAY
                            agent_a.append_connections_array(agent_b.get_id())
                            self.__network.add_edge(agent_a, agent_b, weight= rng.integers(1, 10)/10)
                            # print('AgentA', agent_a.get_id(), ' connections: ', self.__network.num_edges(agent_a),  '/', agent_a_target_connections)
                            # print('AgentB', agent_b.get_id(), ' connections: ', self.__network.num_edges(agent_b),  '/', agent_b_target_connections)
                            iteration_count += 1
                            agent_a_connections = len(agent_a.get_target_connections_array())
                            
                            if agent_a_connections == agent_a_target_connections:
                                break
                        
                        else:
                            pass

                    else:
                        pass
                    agent_a_connections = len(agent_a.get_target_connections_array())
                    iteration_count += 1
            
            yield #for loading bar

    def assign_theory(self):
        
        for agent in self.__context.agents(count=self.__count_of_agents, shuffle=False):
            
            id = agent.get_agent_id()
            dq = agent.get_deprivation_quintile()
            target_connections = agent.get_target_connections_array()
            total_weight = 0

            for agent_id in target_connections:

                agent_b = self.__context.agent((agent_id, 1, 0))
                # print(agent_id)
                # print(agent.get_target_connections_array(), agent_b.get_target_connections_array())
                if self.__network.graph.has_edge(agent, agent_b):
                    edge = self.__network.graph.edges[agent, agent_b]
                    # print(edge['weight'])
                    total_weight += edge['weight']
                # else:
                #     print("No edge between", agent, "and", agent_b)
            
            social_influence = round(total_weight/len(target_connections), 3)
            # print(f'total weight: {total_weight}, social influence: {social_influence}')
            if social_influence > 1:
                raise ValueError('Social influence cannot be greater than 1')
            
            #print(self.__network.num_edges(agent), agent.get_target_connections())
            
            #def __init__(self, id:int, type:int, rank:int, deprivation_quintile:int, sex: int, age: int, drinking_status: int, target_connections: int, space):
            # theory = FundamentalCauseTheory(self.__context, self.__theory_attributes[id]["mean_weekly_units"], self.__theory_attributes[id]["education"], self.__theory_attributes[id]["personal_wealth"], self.__theory_attributes[id]["power"], self.__theory_attributes[id]["prestige"], self.__network.num_edges(agent), social_influence, self.__discrete_space)
            rng = np.random.default_rng(self.__random_seed+id)
            # print(self.__props["drink.distribution.type"])

            if self.__props["drink.distribution.type"] == 1:
                mean_weekly_units = rng.uniform(0, 130)
                mean_weekly_units = round(mean_weekly_units, 3)

            elif self.__props["drink.distribution.type"] == 2:
                mean_weekly_units = rng.normal(25, 10)
                mean_weekly_units = round(mean_weekly_units, 3)
                if mean_weekly_units < 0:
                    mean_weekly_units = -mean_weekly_units
                 
            
            FCT_attributes = generate_theory_vector(dq+1, self.__props["theory.distribution.type"])

            theory = FundamentalCauseTheory(self.__context, mean_weekly_units, FCT_attributes[0], FCT_attributes[1], FCT_attributes[2], FCT_attributes[3], self.__network.num_edges(agent), social_influence, self.__discrete_space)
            
            mediator = SocialTheoriesMediator([theory])

            theory_dict = {
                    "mean_weekly_units": mean_weekly_units,
                    "education": FCT_attributes[0],
                    "personal_wealth": FCT_attributes[1],
                    "knowledge": FCT_attributes[0]/3,
                    "power": FCT_attributes[2],
                    "prestige": FCT_attributes[3],
                    "social_connections":self.__network.num_edges(agent),
                    "social_influence": social_influence,
                    "total_resources": 0,
                    "successful_adaptiation": 0,
                    "unsuccessful_adaptiation": 0
                }
            
            agent.set_theory_array(theory_dict)
            agent.set_params(self.__props)
            agent.set_mediator(mediator)
            theory.set_params(self.__props)
            mediator.set_agent(agent)
            yield

    ############################
    #Loggers
    def log_agents(self): 
        tick = self._runner.schedule.tick
        for agent in self.__context.agents():#get agent starting deprivation quintile
            self.agent_logger.log_row(tick, agent.id, agent.sex, agent.age, agent.get_deprivation_quintile()+1, agent.death_count, agent.get_agent_location()[1], agent.get_agent_location()[0])
        self.agent_logger.write()

# ['mean_weekly_units', 'education', 'personal_wealth', 'social_connections', 'social_influence', 'knowledge', 'strategy_multiplier', 'total_resources', 'successful_adaptiation', 'unsuccessful_adaptiation'])
    def log_theory(self):
        tick = self._runner.schedule.tick
        for agent in self.__context.agents():
            #self.theory_logger = logging.TabularLogger(comm, params['theory.logger'], ['tick', 'id', 'mean_weekly_units', 'education', 'personal_wealth','power', 'prestige', 'social_connections', 'social_influence', 'knowledge', 'total_resources', 'successful_adaptiation', 'unsuccessful_adaptiation'])
            self.theory_logger.log_row(tick, agent.id, agent.get_theory_dict()['mean_weekly_units'], agent.get_theory_dict()['education'], agent.get_theory_dict()['personal_wealth'], agent.get_theory_dict()['power'], agent.get_theory_dict()['prestige'], agent.get_theory_dict()['social_connections'], agent.get_theory_dict()['social_influence'], agent.get_theory_dict()['knowledge'], agent.get_theory_dict()['total_resources'], agent.get_theory_dict()['successful_adaptiation'], agent.get_theory_dict()['unsuccessful_adaptiation'])
        self.theory_logger.write()


    def log_network(self, time):

        new_network = nx.DiGraph()

        # Copy nodes and edges from the existing network object
        # Copy nodes and edges from the existing network object
        for agent in self.__context.agents():
            
            node_attrs = {
                "id": agent.id,  # add a unique ID for each node
                "label": agent.sex,    # add a label for each node based on its type
                "age": agent.age,       # add an age attribute for each node
                "deprivation_quintile": agent.get_deprivation_quintile(),
                "mean_weekly_units": agent.get_theory_dict()['mean_weekly_units'],
                "education": agent.get_theory_dict()['education'],
                "personal_wealth": agent.get_theory_dict()['personal_wealth'],
                "power": agent.get_theory_dict()['power'],
                "prestige": agent.get_theory_dict()['prestige'],
                "social_connections": agent.get_theory_dict()['social_connections'],
                "social_influence": agent.get_theory_dict()['social_influence'],
                "knowledge": agent.get_theory_dict()['knowledge'],
                "total_resources": agent.get_theory_dict()['total_resources'],
                "successful_adaptiation": agent.get_theory_dict()['successful_adaptiation'],
                "unsuccessful_adaptiation": agent.get_theory_dict()['unsuccessful_adaptiation']
                # add more attributes here as needed
            }

            new_network.add_node(agent, **node_attrs)

            for connected_agent_id in agent.get_target_connections_array():
                connected_agent = self.__context.agent((connected_agent_id, 1, 0))
                if connected_agent is not None:
                    new_network.add_edge(agent, connected_agent)


        for agent in self.__context.agents():
            new_network.add_node(agent)
            for connected_agent_id in agent.get_target_connections_array():
                connected_agent = self.__context.agent((connected_agent_id, 1, 0))
                if connected_agent is not None:
                    new_network.add_edge(agent, connected_agent)
        

        yaml = sys.argv[1]
        pattern = r"test_(\d+)\.yaml"

        # Find the match and extract the number
        match = re.search(pattern, yaml)

        if match is None:
            match_num = 0
        else:
            match_num = int(match.group(1))

        output_file = f"FCT_Model/outputs/network/network"+str(match_num)+time+".graphml"
        nx.write_graphml(new_network, output_file)


############################################
#Functions outside the object
def create_FCT_agent(id, type, rank, deprivation_quintile, sex, age, drinking_status, target_connections, space):
    return FCT_Agent(id, type, rank, deprivation_quintile, sex, age, drinking_status, target_connections, space)

# def create_Theory(model.__context, mean_weekly_units_rand, education_rand, personal_wealth_rand, 1, social_influence_rand, self.__discrete_space)
#     return FundamentalCauseTheory(self.__context, mean_weekly_units_rand, education_rand, personal_wealth_rand, 1, social_influence_rand, self.__discrete_space)

def restore_FCT_agent(agent_data):
    uid = agent_data[0]
    return FCT_Agent(uid[0], uid[1], uid[2], agent_data[1])

#############################################################################
#Network Generation

def generate_agent_json_file(num_agents, filename, attributes: Dict[str, list], params, get_data=False, seed_input=1, quintiles=5):
    rng = np.random.default_rng(seed=seed_input)
    agent_data = []
    agent_age_lowest = attributes["age"][0]
    agent_age_highest = attributes["age"][1]
    agent_drinking_lowest = attributes["drinking_status"][0]
    agent_drinking_highest = attributes["drinking_status"][1]

    base_count = num_agents // quintiles
    remaining_agents = num_agents % quintiles

    quintile_labels = np.repeat(np.arange(quintiles), base_count)
    if num_agents % quintiles != 0:
        remaining_labels = rng.choice(np.arange(quintiles), size=num_agents % quintiles, replace=False)
        quintile_labels = np.concatenate((quintile_labels, remaining_labels))


    rng.shuffle(quintile_labels)

    for i in range(num_agents):
        ##### random numbers #####
        sex_rand = int(rng.choice([0, 1], p=[0.5, 0.5]))
        age_rand = int(rng.integers(agent_age_lowest, agent_age_highest))
        agent_drinking_status = int(rng.integers(agent_drinking_lowest, agent_drinking_highest))

        deprivation_quintile_rand = int(quintile_labels[i])


        target_connections_rand = int(rng.integers(3, 4))

        agent = {
            "agent_id": i,
            "agent_type": 1, # all agents are the same type "FCT_agent"
            "rank": 0,# agents are all in the same rank
            "deprivation_quintile": deprivation_quintile_rand,
            "sex": sex_rand,
            "age": age_rand,
            "drinking_status": agent_drinking_status,
            "target_connections": target_connections_rand,
            "space": None
        }

        agent_data.append(agent)

    with open(filename, 'w') as outfile:
        json.dump(agent_data, outfile, indent=4)
    
    with open(filename, 'r') as infile: 
        agent_data = json.load(infile)

    updated_lines = []
    with open('FCT_Model/props/network/graph.txt', 'r') as network_file:
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
    with open('FCT_Model/props/network/graph_updated.txt', 'w') as updated_network_file:
        updated_network_file.writelines(updated_lines)
    
    if get_data:
        return agent_data
    
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
    
#############################################################################

def generate_theory_vector(quintile, distribution_type, pareto_shape=2, normal_std=0.15):
    if not 1 <= quintile <= 5:
        raise ValueError("Quintile must be between 1 and 5")
    if not 1 <= distribution_type <= 3:
        raise ValueError("Distribution type must be between 1 and 3")

    rng = np.random.default_rng()

    # Distribution parameters
    pareto_shape = pareto_shape
    normal_std = normal_std

    base_means = {
        5: (0.5, 1, 0, 0),
        4: (1, 2, 0.25, 0.25),
        3: (1.5, 3, 0.5, 0.5),
        2: (2, 4, 0.75, 0.75),
        1: (2.5, 5, 1, 1)
    }

    mean_education, mean_wealth, mean_power, mean_prestige = base_means[quintile]

    # Define probability distributions
    if distribution_type == 1:  # Uniform
        education = rng.uniform(mean_education, 4)
        wealth = rng.uniform(mean_wealth, 6)
        power = rng.uniform(mean_power, 2)
        prestige = rng.uniform(mean_prestige, 2)

    elif distribution_type == 2:  # Normal
        education = rng.normal(loc=mean_education, scale=normal_std)
        wealth = rng.normal(loc=mean_wealth, scale=normal_std)
        power = rng.normal(loc=mean_power, scale=normal_std)
        prestige = rng.normal(loc=mean_prestige, scale=normal_std)

    elif distribution_type == 3:  # Pareto
        education = rng.pareto(pareto_shape) / pareto_shape + mean_education
        wealth = rng.pareto(pareto_shape) / pareto_shape + mean_wealth
        power = rng.pareto(pareto_shape) / pareto_shape + mean_power
        prestige = rng.pareto(pareto_shape) / pareto_shape + mean_prestige

    # Clip values to their respective valid ranges
    education = np.clip(education, 1, 3)
    wealth = np.clip(wealth, 1, 5)
    power = np.clip(power, 0, 1)
    prestige = np.clip(prestige, 0, 1)

    return [education, wealth/5, power, prestige]

def generate_theory_distributions(type):

    dict = {"mean_weekly_units": [], "education": [], "personal_wealth": []}

    match type:
       
       #changing weekly units
        case 1:# high consumption, normal education, normal wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 2:# normal consumption, normal education, high wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 3:# normal consumption, high education, normal wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 4:# normal consumption, normal education, low wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 5:# normal consumption, low education, normal wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["n"]
            return dict
        case 6:# low consumption, normal education, normal wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 7:# normal consumption, high education, high wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 8:# high consumption, normal education, high wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 9:# high consumption, high education, normal wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 10:# normal consumption, high education, low wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 11:# normal consumption, low education, high wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["p"]
            return dict
        case 12:# high consumption, normal education, low wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 13:# high consumption, low education, normal wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["n"]
            return dict
        case 14:# low consumption, normal education, high wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 15:# low consumption, high education, normal wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 16:# high consumption, low education, low wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["u"]
            return dict
        case 17:# low consumption, high education, low wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 18:# low consumption, low education, high wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["p"]
            return dict
        case 19:# high consumption, high education, high wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 20:# high consumption, high education, low wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 21:# high consumption, low education, high wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["p"]
            return dict
        case 22:# low consumption, high education, high wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 23:# high consumption, low education, low wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["u"]
            return dict
        case 24:# low consumption, high education, low wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 25:# low consumption, low education, high wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["p"]
            return dict
        case 26:# low consumption, low education, low wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["u"]
            return dict
        case _:# normal drinking habits, normal education levels, normal wealth distributions
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["n"] #uniform wealth distribution
            return dict

def get_random_location(file_location, deprivation_quintile, rng_seed):
        #rng = np.random.default_rng(seed=rng_seed)  # create a default Generator instance
        #pos_rand = np.random.default_rng().choice(DQ_1_coords, replace=False)
        match deprivation_quintile:
            case 0:
                DQ_1_coords = find_all_cell_coordinates(file_location, '1')
                pos_rand = np.random.default_rng().choice(DQ_1_coords, replace=False)
                return (pos_rand)
            case 1:
                DQ_2_coords = find_all_cell_coordinates(file_location, '2')
                pos_rand = np.random.default_rng().choice(DQ_2_coords, replace=False)
                return (pos_rand)
            case 2:
                DQ_3_coords = find_all_cell_coordinates(file_location, '3')
                pos_rand = np.random.default_rng().choice(DQ_3_coords, replace=False)
                return (pos_rand)
            case 3:
                DQ_4_coords = find_all_cell_coordinates(file_location, '4')
                pos_rand = np.random.default_rng().choice(DQ_4_coords, replace=False)
                return (pos_rand)
            case 4:
                DQ_5_coords = find_all_cell_coordinates(file_location, '5')
                pos_rand = np.random.default_rng().choice(DQ_5_coords, replace=False)
                return (pos_rand)
            case _:
                raise ValueError("Deprivation quintile must be between 0 and 4")
        
        #print(DQ_1_coords[pos_rand][0], DQ_1_coords[pos_rand][1])
        #print(len(DQ_1_coords) ,len(DQ_2_coords), len(DQ_3_coords), len(DQ_4_coords), len(DQ_5_coords))

def find_all_cell_coordinates(csv_file, target_value):
    coordinates = []
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        for row_num, row in enumerate(reader):
            for col_num, cell_value in enumerate(row):
                if cell_value == target_value:
                    coordinates.append((row_num+1, col_num+1))# +1 so that they don't start at 0
    return coordinates

def get_unique_random_coordinate(coordinates, used_coordinates):
    available_coordinates = [coord for coord in coordinates if coord not in used_coordinates]

    if not available_coordinates:
        print("No more unique coordinates available.")
        return None

    random_coordinate = random.choice(available_coordinates)
    used_coordinates.add(random_coordinate)
    return random_coordinate


