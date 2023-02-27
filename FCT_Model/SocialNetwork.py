"""
This section of code shall be used to implement the social element of the model, ie the SocialNetwork class.
The code is adapted from the 'rumor' example program https://repast.github.io/repast4py.site/guide/user_guide.html#_tutorial_2_the_rumor_network_model

"""

import networkx as nx

from typing import Dict
from mpi4py import MPI
import numpy as np


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
    n_ranks = 5

    # Generate the network file if it doesn't exist
    fname = "FCT_Model/props/network/FCT_network.txt"
    generate_network_file(fname, n_ranks, n_agents)




def generate_network_file(fname: str, n_ranks: int, n_agents: int):
    """Generates a network file using repast4py.network.write_network.

    Args:
        fname: the name of the file to write to
        n_ranks: the number of process ranks to distribute the file over
        n_agents: the number of agents (node) in the network
    """


    g = nx.connected_watts_strogatz_graph(n_agents, 2, 0.25)

    fname = "FCT_Model/props/network/"
    try:
        import nxmetis
        write_network(g, 'FCT_network', fname, n_ranks, partition_method='metis')
    except ImportError:
        write_network(g, 'FCT_network', fname, n_ranks)


if __name__ == "__main__":
    main()
