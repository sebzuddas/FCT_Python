import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import os
import mysql.connector
import sys
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from  dash import dcc
from dash import html
import networkx as nx
import visdcc
import json
import math
from zipfile import ZipFile

import plotly.io as pio
import flask
import io

import search

host_var='127.0.0.1'
user_var = str(os.environ['MYSQL_USER'])
password_var = str(os.environ['MYSQL_PASSWORD'])
database_var='simulation_data'
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
project_path = str(os.environ['FCT_PROJECT_FOLDER'])
color_scale = ['#398278', '#97af87', '#d3c668', '#db9e63', '#bf5b32']
#398278, #a0bb9c, #d3c668, #eaaa7a, #bf5b32
#00d700, #00ffca, yellow, #ff7f00, red

#398278, #97af87, #d3c668, #db9e63, #bf5b32

bar_colours_good = ['#24dcc1', '#2fc4ae', '#36ae9c', '#38988a', '#398278']
bar_colours_bad = ['#d79840', '#d1883f', '#cb793e', '#c56a3d', '#bf5b32']
line_colours_good = ['#24dcc1', '#a4a4a4', '#8e8e8e', '#787878', '#398278']
line_colours_bad = ['#d79840', '#a4a4a4', '#8e8e8e', '#787878', '#bf5b32']

#bf5b32, #c56a3d, #cb793e, #d1883f, #d79840


font_dict = dict(
        family='serif',
        size=18,
        color='black'
    )
legend_dict = dict(
    font=dict(
        size=11,  # decrease font size
    ),
    orientation="h",
    yanchor="bottom",
    y=1,  # May need adjustment depending on your specific figure
    xanchor="left",
    x=0
)



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
        # print(node)

    return sorted_nodes
    
def get_nodes_edges_from_graphml(file_path):
    # Read the GraphML file
    str(file_path)
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

# def assign_color_and_level(node_label):
#     # d3 is deprivation quintile
#     if node_label == 0:
#         return {"color": color_scale[0], "level": 0}
#     elif node_label == 1:
#         return {"color": color_scale[1], "level": 1}
#     elif node_label == 2:
#         return {"color": color_scale[2], "level": 2}
#     elif node_label == 3:
#         return {"color": color_scale[3], "level": 3}
#     elif node_label == 4:
#         return {"color": color_scale[4], "level": 4}

def assign_color(deprivation_quintile):
    color_map = {
        0: color_scale[0],
        1: color_scale[1],
        2: color_scale[2],
        3: color_scale[3],
        4: color_scale[4]
    }
    return color_map[deprivation_quintile]


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
     Output("graph-1_1", "figure"),
     Output("graph-2", "figure"),
     Output("graph-2_1", "figure"),
     Output("graph-3", "figure")],
    [Input("simulation-dropdown", "value")],
)
def update_graphs(selected_simulation):
    
    # Load the data for the selected_simulation
    # Modify the following lines to load the correct data
    # You can replace these example figures with the figures you want to display for each simulation
    # print("selected simulation: ", selected_simulation)
    # print(sorted_simulations)
    filtered_gradients = pd.DataFrame(sorted_simulations[sorted_simulations['Simulation'] == selected_simulation])
    # print(filtered_gradients)
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
    # print(total_deaths)
    
    total_deaths_melted = total_deaths.reset_index().melt(id_vars='deprivation_quintile', var_name='tick', value_name='value')
    total_deaths_melted = total_deaths_melted.sort_values(['deprivation_quintile', 'tick'])
    # Create a new DataFrame that only includes the rows where 'value' changes within each 'deprivation_quintile'
    total_deaths_changed = total_deaths_melted[total_deaths_melted['value'].diff() != 0]
    # The first row for each 'deprivation_quintile' is removed because it's not a real change
    total_deaths_changed = total_deaths_changed[total_deaths_changed['deprivation_quintile'].eq(total_deaths_changed['deprivation_quintile'].shift())]
    total_deaths_changed['cumulative_value'] = total_deaths_changed.groupby('deprivation_quintile')['value'].cumsum()
    #get the last cumulative sum of deaths over the simulation
    total_deaths_sim = total_deaths_changed.groupby('deprivation_quintile')['cumulative_value'].last()

    # print(total_deaths_changed)

    # print(total_deaths_sim)




    total_deaths_figure = go.Figure()

    total_deaths_figure.add_trace(
        go.Bar(
            x=total_deaths_sim.index,
            y=total_deaths_sim.values,
            marker=dict(color=total_deaths_sim.index, colorscale=color_scale),
            name=''
        )
    )

    x_death_tot = np.sort(total_deaths_sim.index)
    death_gradient = search.get_gradient(total_deaths_sim.index, total_deaths_sim.values)
    y_death_tot = death_gradient * (x_death_tot - x_death_tot[0]) + total_deaths_sim.values[np.argsort(total_deaths_sim.index)][0]

    total_deaths_figure.add_trace(go.Scatter(x=x_death_tot, y=y_death_tot, mode='lines', name='Death Gradient Line'))

    total_deaths_figure.update_layout(
        yaxis_title='Total Deaths',
        xaxis_title='Deprivation Quintile',
        title=f'Total Deaths per Deprivation Quintile from Simulation {selected_simulation}',
        legend=legend_dict,
        font=font_dict
    )

    deaths_over_time_figure = px.line(total_deaths_changed, x='tick', y='cumulative_value', color='deprivation_quintile', color_discrete_sequence=color_scale, title=f"Deaths over Time from Simulation {selected_simulation}")
    deaths_over_time_figure.update_layout(
        yaxis_title='Cumulative Deaths',
        xaxis_title='Ticks',
        title=f'Deaths per Deprivation Quintile over Time from Simulation {selected_simulation}',
        legend=legend_dict,
        font=font_dict,
        yaxis_type="log", # log scale for y-axis
        xaxis_type="log", # log scale for x-axis
        )




    ##### Adaptation Graph #####
    # 1. Get successful and unsuccessful adaptation data
    successful_adaptation_data = search.get_data_by_dq(data, ['successful_adaptiation'], pivot=False)
    unsuccessful_adaptation_data = search.get_data_by_dq(data, ['unsuccessful_adaptiation'], pivot=False)

    # 2. Merge the successful and unsuccessful adaptation data
    adaptation_data = pd.merge(successful_adaptation_data, unsuccessful_adaptation_data, on=['deprivation_quintile', 'tick'])

    # 3. Calculate the adaptation ratio
    adaptation_data['adaptation_ratio'] = adaptation_data['unsuccessful_adaptiation'] / (adaptation_data['successful_adaptiation'] + adaptation_data['unsuccessful_adaptiation'])

    # Calculate the cumulative sum of successful and unsuccessful adaptations for each deprivation quintile
    adaptation_data['successful_cumsum'] = adaptation_data.groupby('deprivation_quintile')['successful_adaptiation'].cumsum()
    adaptation_data['unsuccessful_cumsum'] = adaptation_data.groupby('deprivation_quintile')['unsuccessful_adaptiation'].cumsum()
    adaptation_data['adaptation_ratio_cumsum'] = adaptation_data['successful_cumsum'] / (adaptation_data['successful_cumsum'] + adaptation_data['unsuccessful_cumsum'])
    # Use groupby to group by deprivation_quintile and get the last entry of each group
    end_simulation_data = adaptation_data.groupby('deprivation_quintile').last().reset_index()

    # print(adaptation_data)
    # Print the new DataFrame
    # print(end_simulation_data)

    # adaptation_gradient = filtered_gradients['Adaptation Gradient'].iloc[0]
    # Calculate the gradient
    adaptation_gradient = search.get_gradient(end_simulation_data['deprivation_quintile'], end_simulation_data['adaptation_ratio_cumsum'])
    x_adapt_tot = np.sort(end_simulation_data['deprivation_quintile'])

    # Calculate the y values for the fitted line
    y_adapt_tot = adaptation_gradient * (x_adapt_tot - x_adapt_tot[0]) + end_simulation_data['adaptation_ratio_cumsum'].values[np.argsort(end_simulation_data['deprivation_quintile'])][0]

    # Create the scatter plot

    adaptation_total_figure = go.Figure()

    # your gradient line
    adaptation_total_figure.add_trace(go.Scatter(x=x_adapt_tot, y=y_adapt_tot, mode='lines', name='Adaptation Gradient Line'))

    # Successful adaptations
    adaptation_total_figure.add_trace(
        go.Bar(
            x=end_simulation_data['deprivation_quintile'],
            y=end_simulation_data['successful_adaptiation'],
            name='Successful Adaptations',
            marker=dict(color=bar_colours_good, showscale=False)
        )
    )

    # Unsuccessful adaptations
    adaptation_total_figure.add_trace(
        go.Bar(
            x=end_simulation_data['deprivation_quintile'],
            y=-end_simulation_data['unsuccessful_adaptiation'],
            name='Unsuccessful Adaptations',
            marker=dict(color=bar_colours_bad, showscale=False)
        )
    )

    # Update the figure layout to include a legend
    adaptation_total_figure.update_layout(
        xaxis_title='Deprivation Quintile',
        yaxis_title='Total Adaptations',
        title=f'Total Adaptations per Deprivation Quintile from Simulation {selected_simulation}',
        legend=legend_dict,
        font=font_dict,
    )
    
    adaptation_over_time_figure = go.Figure()

    for i in range(1, 6):
        # Filter the data for the current deprivation quintile
        df = adaptation_data[adaptation_data['deprivation_quintile'] == i]

        # Add a line for successful adaptations
        adaptation_over_time_figure.add_trace(
            go.Scatter(
                x=df['tick'],
                y=df['successful_adaptiation'],
                mode='lines',
                name=f'Successful Adaptations Q{i}',
                line=dict(color=line_colours_good[i-1])
            )
        )

        # Add a line for unsuccessful adaptations
        adaptation_over_time_figure.add_trace(
            go.Scatter(
                x=df['tick'],
                y=df['unsuccessful_adaptiation'],
                mode='lines',
                name=f'Unsuccessful Adaptations Q{i}',
                line=dict(color=line_colours_bad[i-1])
            )
        )




        adaptation_over_time_figure.update_layout(yaxis_title='Total Adaptations per Deprivation Quintile',
        xaxis_title='Ticks',
        title='Total Adaptations over Time per Deprivation Quintile',
        legend=legend_dict,
        font=font_dict,
        coloraxis_colorbar=None
        )

    

    ##### Consumption Graph #####

    total_consumption = search.get_data_by_dq(data,['mean_weekly_units'], pivot=True)
    total_consumption_reset = total_consumption.reset_index().melt(id_vars='deprivation_quintile', var_name='tick', value_name='value')
    mean_consumption_tick = total_consumption.div(200)# average consumption every tick by deprivation quintiles
    mean_consumption_tot = mean_consumption_tick.sum(axis=1) / 520# average consumption throughout the simulation by deprivation quintiles
    
    # consumption_gradient = filtered_gradients['Consumption Gradient'].iloc[0]
    
    consumption_gradient = search.get_gradient(mean_consumption_tot.index, mean_consumption_tot.values)

    consumption_total_figure = go.Figure()

    consumption_total_figure.add_trace(
        go.Bar(
            x=mean_consumption_tot.index,
            y=mean_consumption_tot.values,
            marker=dict(color=total_deaths_sim.index, colorscale=color_scale),
            name=''
        )
    )

    x_consum_tot = np.sort(mean_consumption_tot.index)
    y_consum_tot = consumption_gradient * (x_consum_tot - x_consum_tot[0]) + mean_consumption_tot.values[np.argsort(total_deaths_sim.index)][0]

    consumption_total_figure.add_trace(go.Scatter(x=x_consum_tot, y=y_consum_tot, mode='lines', name='Consumption Gradient Line'))

    consumption_total_figure.update_layout(
        yaxis_title='Total Consumption',
        xaxis_title='Deprivation Quintile',
        title=f'Total Consumption per Deprivation Quintile from Simulation {selected_simulation}',
        legend=legend_dict,
        font=font_dict
    )

    return total_deaths_figure, deaths_over_time_figure, adaptation_total_figure, adaptation_over_time_figure, consumption_total_figure

@app.callback(
    [Output("network", "figure"),Output('network-stats', 'children')],
    Input("simulation-dropdown", "value")
    )
def update_network_graph(selected_simulation):
    graph_stats = []

    network_location = "network"+str(selected_simulation)+"start.graphml"
    individual_network = project_path+"FCT_Model/outputs/network/"+network_location

    intermediate_nodes, edges, G = get_nodes_edges_from_graphml(individual_network)
    nodes = circular_coordinates(intermediate_nodes)

    for node in nodes:
        node_id = node['id']  # assuming 'id' is the key that identifies the node
        G.nodes[node_id]['pos'] = (node['x'], node['y'])


    for node in G.nodes():
        node_attributes = G.nodes[node]
        pos_value = node_attributes['pos']
        # Access the 'x' and 'y' values within the 'pos' attribute
        x_value, y_value = pos_value
        # Assign the 'pos' attribute with the 'x' and 'y' values
        G.nodes[node]['pos'] = (x_value, y_value)
        # print(node)
        # print(G.nodes[node]["deprivation_quintile"])
        deprivation_quintile = G.nodes[node]["deprivation_quintile"]
        G.nodes[node]['color'] = assign_color(deprivation_quintile)
        # node["shape"] = "dot"
        # node["size"] = 10
        # node["mass"] = 1
        # print(node)
        
    #Graph statistics
    # Calculate network statistics
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = nx.density(G)
    diameter = nx.diameter(G)
    average_clustering = nx.average_clustering(G)
    average_degree = sum(dict(G.degree()).values()) / float(len(G))
    degree_distribution = [degree for (node, degree) in G.degree()]
    degree_centrality = nx.degree_centrality(G)
    katz_centrality = nx.katz_centrality(G)

    print(num_nodes)
    print(num_edges)
    print(density)
    print(diameter)
    print(average_clustering)
    print(average_degree)
    print(katz_centrality)
    # betweenness_centrality = nx.betweenness_centrality(G)
    # print(betweenness_centrality)
    # # closeness_centrality = nx.closeness_centrality(G)
    # print(closeness_centrality)

    # print(degree_distribution)
    # print(degree_centrality)




    graph_stats = [html.P(f"Number of nodes: {num_nodes}"),
                   html.P(f"Number of edges: {num_edges}"),
                   html.P(f"Density: {density:.4f}"),
                   html.P(f"Diameter: {diameter}"),
                   html.P(f"Average clustering: {average_clustering:.4f}")]


    edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5, color="#888"),
    hoverinfo="none",
    mode="lines")

    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_trace["x"] += tuple([x0, x1, None])
        edge_trace["y"] += tuple([y0, y1, None])


    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=False,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title="Node Connections",
                xanchor="left",
                titleside="right"
            ),
            line=dict(width=0)))
        
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])
        node_info = f'Node {node}<br /># of connections: {len(list(G.neighbors(node)))}'
        node_trace['text'] += tuple([node_info])
        node_trace['marker']['color'] += tuple([G.nodes[node]['color']])
    
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                    title=f'Network for Simulation {selected_simulation}',
                    font= font_dict,
                    titlefont=dict(size=18),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    # marker=dict(showscale=False),
                    # annotations=[ dict(
                    #     # text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                    #     showarrow=False,
                    #     xref="paper", yref="paper",
                    #     x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))

                    )
    return fig, graph_stats


def main():
    app.layout = html.Div(
        [
            html.H1("The Alcohol Harm Paradox Visualised"),
            html.H2("Please Select a Simulation to View"),
                dcc.Dropdown(
                    id="simulation-dropdown",
                    options=available_simulations,
                    value=1,  # Default value
                    style={"width": "50%"},
            ),
            html.Div(
                [
                    # html.H3("Network Statistics"),
                    # html.P(f"Number of nodes: {num_nodes}"),
                    # html.P(f"Number of edges: {num_edges}"),
                    # html.P(f"Density: {density:.4f}"),
                    # html.P(f"Diameter: {diameter}"),
                    # html.P(f"Average clustering: {average_clustering:.4f}")
                    # html.P(f"Degree centrality: {degree_centrality}"),
                    # html.P(f"Betweeness centrality: {betweeness_centrality}"),
                    # html.P(f"Closeness centrality: {closeness_centrality}"),
                    #TODO: average outdegree per quintile. 
                    #TODO: For all agents whats the average outdegree for same quintile links vs different quinitle links. 
                    # Add more statistics as needed
                ],
                style={"margin-bottom": "20px", "width": "80%"},
            ),
            html.H2("Network"),
            dcc.Graph(id="network"),
            html.Div(id='network-stats',
            style={"margin-bottom": "20px", "width": "80%"}),
            html.Div(
            children=[
                html.H3("Death Data"),
                html.H4("Deaths by Deprivation Quintile"),
                dcc.Graph(id="graph-1"),
                html.H4("Deaths Over Time"),
                dcc.Graph(id="graph-1_1"),


                html.H3("Adaptation Data"),
                html.H4("Adaptation by Deprivation Quintile"),
                dcc.Graph(id="graph-2"),
                html.H4("Adaptation Over Time"),
                dcc.Graph(id="graph-2_1"),


                html.H3("Consumption Data"),
                dcc.Graph(id="graph-3"),
                # Add more graphs as needed

                html.Button('Save as PNG', id='btn'),
                html.A(id='link')
            ],
            style={"width": "80%"},
        ),
    ]
)




@app.callback(
    Output('link', 'href'),
    Output('link', 'download'),
    [Input('btn', 'n_clicks')],
    [State('network', 'figure'),
     State('graph-1', 'figure'),
     State('graph-1_1', 'figure'),
     State('graph-2', 'figure'), 
     State('graph-2_1', 'figure'),
     State('graph-3', 'figure'),],
    prevent_initial_call=True
)
def save_as_png(n_clicks, fig1, fig2, fig3, fig4, fig5, fig6):
    if n_clicks is not None:
        # Ensure the 'static' directory exists
        os.makedirs('static', exist_ok=True)
        # Save figures to Flask's "static" directory
        for i, fig in enumerate([fig1, fig2, fig3, fig4, fig5, fig6], start=1):
            img_bytes = pio.to_image(fig, format='png', scale=4.17)
            with open(f"static/plot_image_{i}.png", 'wb') as f:
                f.write(img_bytes)
        return '/download_image', 'plot_image.zip'


@app.server.route('/download_image')
def serve_image():
    # Create a ZIP file of all images
    with ZipFile('static/plot_images.zip', 'w') as zipf:
        for i in range(1, 7):  # adjust this range to the number of figures
            zipf.write(f'static/plot_image_{i}.png')
    return flask.send_file('static/plot_images.zip', mimetype='application/zip')




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