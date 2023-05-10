import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import os
import mysql.connector
import sys
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from  dash import dcc
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

def get_simulation_data(experiment_number, db_config):
    #get simulation data from database
    #connect to database
    

    if experiment_number !=0:
        #get specific experiment
        pass
    else:
        #get all experiments
        pass






def display_harms(df):
    pass

def animate_simulation(sim_number):
    #animate the x,y values of the simulation using dash
    pass


@app.callback(
    [Output("graph-1", "figure"),
     Output("graph-2", "figure"),
     Output("graph-3", "figure")],
    [Input("simulation-dropdown", "value")],
)
def update_graphs(selected_simulation):
    # Load the data for the selected_simulation
    # Modify the following lines to load the correct data
    # You can replace these example figures with the figures you want to display for each simulation
    filtered_gradients = pd.DataFrame(sorted_simulations[sorted_simulations['Simulation'] == selected_simulation])
    filtered_gradients['Death Gradient'] = [float(x.strip('[]')) for x in filtered_gradients['Death Gradient']]
    filtered_gradients['Consumption Gradient'] = [float(x.strip('[]')) for x in filtered_gradients['Consumption Gradient']]
    filtered_gradients['Adaptation Gradient'] = [float(x.strip('[]')) for x in filtered_gradients['Adaptation Gradient']]
    filtered_gradients = filtered_gradients.astype(float)
    filtered_gradients = filtered_gradients.round(4)

    data, headers = search.get_database_tables(selected_simulation, db_config)
    
    for header in headers:
        if not header.startswith('simulation'):
            data[header] = pd.to_numeric(data[header])
    
    ##### Death Graph #####
    total_deaths = search.get_data_by_dq(data,['death_count'], pivot=True)
    total_deaths_sim = total_deaths.iloc[:, -1]#Total deaths by deprivation quintile by the end of the simulation
    death_gradient = filtered_gradients['Death Gradient'].iloc[0]

    total_deaths_figure = px.bar(x=total_deaths_sim.index, y=total_deaths_sim.values, title=f"Total Deaths from Simulation {selected_simulation}")

    # Sort the x-axis values for the Death Gradient line
    x_death_tot = np.sort(total_deaths_sim.index)

    # Calculate the y values for the fitted line
    y_death_tot = death_gradient * (x_death_tot - x_death_tot[0]) + total_deaths_sim.values[np.argsort(total_deaths_sim.index)][0]

    # Add a trace for the Death Gradient line
    total_deaths_figure.add_trace(go.Scatter(x=x_death_tot, y=y_death_tot, mode='lines', name='Death Gradient Line'))


    # Update the figure layout to include a legend
    total_deaths_figure.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="right",
        x=1
    ))



    ##### Adaptation Graph #####
    #adaptation_data = data.groupby(['deprivation_quintile', 'tick']).agg({'successful_adaptiation': 'sum', 'unsuccessful_adaptiation': 'sum'}).reset_index()
    # adaptation_data = data.groupby(['deprivation_quintile', 'tick']).agg({'successful_adaptiation': 'sum', 'unsuccessful_adaptiation': 'sum'}).reset_index()
    adaptation_data = search.get_data_by_dq(data,['successful_adaptiation', 'unsuccessful_adaptiation'], pivot=False)
    # print(adaptation_data)
    adaptation_data['adaptation_ratio'] = adaptation_data['successful_adaptiation'] / (adaptation_data['successful_adaptiation'] + adaptation_data['unsuccessful_adaptiation'])
    adaptation_data = adaptation_data.pivot(index='tick', columns='deprivation_quintile', values='adaptation_ratio')
    # print(adaptation_data)
    adaptation_total = adaptation_data.iloc[-1, :]#Total adaptation ratio by deprivation quintile by the end of the simulation
    # print(adaptation_total)

    adaptation_gradient = filtered_gradients['Adaptation Gradient'].iloc[0]

    adaptation_total_figure = px.bar(x=adaptation_total.index, y=adaptation_total.values, title=f"Total Adaptations from Simulation {selected_simulation}")

    # Sort the x-axis values for the Death Gradient line
    x_adapt_tot = np.sort(adaptation_total.index)

    # Calculate the y values for the fitted line
    y_adapt_tot = adaptation_gradient * (x_adapt_tot - x_adapt_tot[0]) + adaptation_total.values[np.argsort(total_deaths_sim.index)][0]

    # Add a trace for the Death Gradient line
    adaptation_total_figure.add_trace(go.Scatter(x=x_adapt_tot, y=y_adapt_tot, mode='lines', name='Adaptation Gradient Line'))
    # adaptation_total_figure.add_bar(go.bar(x=)) # add the unsuccessful ones to the bar
    # Update the figure layout to include a legend
    adaptation_total_figure.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="right",
        x=1
    ))


    ##### Consumption Graph #####

    total_consumption = search.get_data_by_dq(data,['mean_weekly_units'], pivot=True)
    mean_consumption_tick = total_consumption.div(200)# average consumption every tick by deprivation quintiles
    mean_consumption_tot = mean_consumption_tick.sum(axis=1) / 1040# average consumption throughout the simulation by deprivation quintiles
    consumption_gradient = filtered_gradients['Consumption Gradient'].iloc[0]

    consumption_total_figure = px.bar(x=mean_consumption_tot.index, y=mean_consumption_tot.values, title=f"Total Consumption from Simulation {selected_simulation}")
    x_consum_tot = np.sort(mean_consumption_tot.index)

    # Calculate the y values for the fitted line
    y_consum_tot = consumption_gradient * (x_consum_tot - x_consum_tot[0]) + mean_consumption_tot.values[np.argsort(total_deaths_sim.index)][0]

    # Add a trace for the Death Gradient line
    consumption_total_figure.add_trace(go.Scatter(x=x_consum_tot, y=y_consum_tot, mode='lines', name='Consumption Gradient Line'))
    # Update the figure layout to include a legend
    consumption_total_figure.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="right",
        x=1
    ))


    return total_deaths_figure, adaptation_total_figure, consumption_total_figure






def main():
    # Load the network data for the selected_simulation
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

    # node_coordinates =circular_coordinates(intermediate_nodes)

    #Graph statistics
    # Calculate network statistics
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = nx.density(G)
    diameter = nx.diameter(G)
    average_clustering = nx.average_clustering(G)
    # degree_centrality = nx.degree_centrality(G)
    # betweeness_centrality = nx.betweenness_centrality(G)
    # closeness_centrality = nx.closeness_centrality(G)

    app.layout = html.Div(
        [
            html.H1("Network Visualisation and Data"),
                dcc.Dropdown(
                    id="simulation-dropdown",
                    options=available_simulations,
                    value=1,  # Default value
                    style={"width": "50%"},
            ),
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
                style={"margin-bottom": "20px", "width": "80%"},
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
            html.Div(
            children=[
                html.H3("Death Data"),
                dcc.Graph(id="graph-1"),
                html.H3("Adaptation Data"),
                dcc.Graph(id="graph-2"),
                html.H3("Consumption Data"),
                dcc.Graph(id="graph-3"),
                # Add more graphs as needed
            ],
            style={"width": "80%"},
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

    gradient_path = os.path.join(project_path, 'Data_Processing/outputs/gradients/sorted_gradients.csv')

    if not os.path.exists(gradient_path):
        sorted_simulations = search.find_ahp(db_config)    
    else:
    # Load the CSV file into a Pandas DataFrame
        sorted_simulations = pd.read_csv(gradient_path)



    available_simulations = [{"label": f"Simulation {i}", "value": i} for i in range(1, len(sorted_simulations))]  # Replace this with the list of available simulations from your database
    
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