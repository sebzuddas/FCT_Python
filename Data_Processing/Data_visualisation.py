import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import os
import mysql.connector
import sys
import dash
import dash_bootstrap_components as dbc
from dash import html
import networkx as nx
import visdcc
import json
import math

import search

host_var='127.0.0.1'
user_var = str(os.environ['MYSQL_USER'])
password_var = str(os.environ['MYSQL_PASSWORD'])
database_var='simulation_data'
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
project_path = str(os.environ['FCT_PROJECT_FOLDER'])



#### Dash App ####




#### Data Processing ####





# fig2 = px.bar(total_deaths, x=total_deaths.index, y=total_deaths.columns.max())
    # fig2.update_layout(yaxis_title='Total Deaths', xaxis_title='Deprivation Quintile', title='Total Deaths per Deprivation Quintile', font=dict(
    #     family='serif',
    #     size=18,
    #     color='black'
    # ))

# fig2.show()

    # fig3 = px.bar(total_consumption, x=total_consumption.index, y=total_consumption.columns.max())

    # fig3.update_layout(yaxis_title='Consumption', xaxis_title='Deprivation Quintile', title='Total Consumption per Deprivation Quintile', font=dict(
    #     family='serif',
    #     size=18,
    #     color='black'
    # ))

    # fig3.show()


#to show regression line, harm wrt deprivation quintile
    # df = pd.DataFrame({'X': X.flatten(), 'y': y.flatten()})
    # fig = px.scatter(df, x='X', y='y', trendline='ols')
    # fig.show()



def circular_coordinates(intermediate_nodes, radius=300):
    num_groups = 5
    total_nodes = len(intermediate_nodes)
    angle_step = 2 * math.pi / total_nodes

    # Sort nodes by their group property
    sorted_nodes = sorted(intermediate_nodes, key=lambda x: x["group"])

    # Assign coordinates for each node based on the order in the sorted list
    for i, node in enumerate(sorted_nodes):
        angle = i * angle_step
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        node["x"] = x
        node["y"] = y
        node["fixed"] = {"x": True, "y": True}

    return sorted_nodes


# def get_nodes_edges_from_graphml(file_path, node_coordinates):
#     # Read the GraphML file
#     G = nx.read_graphml(file_path)
# # Extract nodes and edges
# nodes = [
#     {
#         "id": str(node),
#         "label": str(node),
#         "group": int(G.nodes[node]["d3"]),
#         "color": colors[int(G.nodes[node]["d3"])],
#         "x": node_coordinates[str(node)]["x"],
#         "y": node_coordinates[str(node)]["y"],
#         "fixed": {"x": True, "y": True},
#     }
#     for node in G.nodes()
# ]

# # Extract nodes and edges
# edges = [{"from": str(edge[0]), "to": str(edge[1])} for edge in G.edges()]

# return nodes, edges


    
def get_nodes_edges_from_graphml(file_path):
    # Read the GraphML file
    G = nx.read_graphml(file_path)
    

    # Extract nodes and edges
    intermediate_nodes = [
        {
            "id": str(node),
            "group": int(G.nodes[node]["deprivation_quintile"]),
        }
        for node in G.nodes()
    ]
    edges = [{"from": str(edge[0]), "to": str(edge[1])} for edge in G.edges()]

    return intermediate_nodes, edges, G

def assign_color_and_level(node_label):
    #d3 is deprivation quintile
    if node_label.startswith("A"):
        return {"color": "red", "level": 0}
    elif node_label.startswith("B"):
        return {"color": "blue", "level": 1}
    else:
        return {"color": "green", "level": 2}

def get_simulation_data(experiment_number):

    if experiment_number !=0:
        #get specific experiment
        pass
    else:
        #get all experiments
        pass


def display_network(df):
    pass

def display_harms(df):
    pass

def animate_simulation(sim_number):
    #animate the x,y values of the simulation using dash
    pass


def main():
    # Create a Dash app

    network_location = f"network<re.Match object; span=(38, 49), match='test_{experiment_number}.yaml'>_start.graphml"
    individual_network = project_path+"FCT_Model/outputs/network/"+network_location

    intermediate_nodes, edges, G = get_nodes_edges_from_graphml(individual_network)
    nodes = circular_coordinates(intermediate_nodes)
    colors = ["red", "orange", "yellow", "lightgreen", "green"]

    # Add the color and label properties to the nodes list
    for node in nodes:
        

        node["color"] = colors[node["group"]]
        node["shape"] = "dot"
        node["size"] = 10
        node["mass"] = 1
        # node["level"] = assign_color_and_level(node["label"])["deprivation_quintile"]

    # node_coordinates =circular_coordinates(intermediate_nodes)

    #Graph statistics
    # Calculate network statistics
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = nx.density(G)
    diameter = nx.diameter(G)
    average_clustering = nx.average_clustering(G)
    degree_centrality = nx.degree_centrality(G)
    betweeness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)


    # Add more statistics as needed





    # Define the app layout
    app.layout = html.Div(
        [
            html.H1("Network Visualization with Dash and visdcc"),
            html.Div(
                [
                    html.H3("Network Statistics"),
                    html.P(f"Number of nodes: {num_nodes}"),
                    html.P(f"Number of edges: {num_edges}"),
                    html.P(f"Density: {density:.4f}"),
                    html.P(f"Diameter: {diameter}"),
                    html.P(f"Average clustering: {average_clustering:.4f}")
                    # html.P(f"Degree centrality: {degree_centrality}"),
                    # html.P(f"Betweeness centrality: {betweeness_centrality}"),
                    # html.P(f"Closeness centrality: {closeness_centrality}"),
                    # Add more statistics as needed
                ],
                style={"margin-bottom": "20px"},
            ),
            visdcc.Network(
                id="network",
                options=dict(height="600px", 
                             width="100%", 
                             physics={
                                "enabled": False
                            },
                             edges={
                            "smooth": {
                                "type": "continuous",
                                "forceDirection": "none",
                                "roundness": 1
                            },
                            "length": 150,  # Adjust edge length (smaller values for shorter edges)
                            },),
                data=dict(nodes=nodes, edges=edges),

            ),

        ]
    )




if __name__ == "__main__":

    db_config = {
        'user': user_var,
        'password': password_var,
        'host': host_var,
        'database': database_var,
    }
    sorted_simulations = search.find_ahp(db_config)
    print(sorted_simulations)
    

    experiment_number = sys.argv[1]
    # if display_type == 'network':
    #     display_network()
    # elif display_type == 'harms':
    #     display_harms()
    # elif display_type == 'animate':
    #     animate_simulation()
    # else:
    #     print('Invalid display type. Please enter either "network", "harms" or "animate"')
    #     sys.exit()
    main()
    app.run_server(debug=True)