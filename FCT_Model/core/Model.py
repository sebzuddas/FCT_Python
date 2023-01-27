from __future__ import annotations
from typing import Dict, List
from abc import abstractmethod, ABCMeta

from repast4py import context, schedule
import repast4py

from .StructuralEntity import StructuralEntity
from .MicroAgent import MicroAgent


class Model(metaclass=ABCMeta):

    def __init__(self, comm, params: Dict):
        self.__props = params
        self.stop_at:int = self.__props["stop.at"] if "stop.at" in params else 0
        self._count_of_agents:int = self.__props["count.of.agents"] if "count.of.agents" in params else 0

        self.__context = None
        self.__structural_entity_list: List[StructuralEntity] = []
        # Repast4py lacks some of the singletons available in repastHPC, so the runner is a member of the Model class.
        self.__runner: repast4py.schedule.SharedScheduleRunner = repast4py.schedule.init_schedule_runner(comm)


    @abstractmethod
    def init_agents(self):
        pass

    def init_schedule(self):
        self.__runner.schedule_repeating_event(1, 1, self.do_per_tick)
        self.__runner.schedule_stop(self.stop_at)

    def do_situational_mechanisms(self):
        for agent in self.__context.agents(MicroAgent.TYPE, shuffle=False):
            agent.do_situation()
    
    def do_action_mechanisms(self):
        for agent in self.__context.agents(MicroAgent.TYPE, shuffle=False):
            agent.do_action()
    
    def do_transformational_mechanisms(self):
        for structural_entity in self.__structural_entity_list:
            structural_entity.do_transformation()
    
    def do_per_tick(self):
        self.do_situational_mechanisms()
        self.do_action_mechanisms()
        self.do_transformational_mechanisms()

    def run(self):
        self.__runner.execute()