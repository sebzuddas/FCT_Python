"""
Main file for processing the outputted data from the FCT_Model

"""
import sys
import pandas as pd
import plotly.express as px
import yaml
import kaleido
import plotly.graph_objects as go

import dash 
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import numpy as np
import mysql.connector
import requests
import os


host_var='127.0.0.1'
user_var = str(os.environ['MYSQL_USER'])
password_var = str(os.environ['MYSQL_PASSWORD'])
database_var='simulation_data'




def load_agent_data(simulation_id, agent_id):# reads individual agent data based on an agent ID
    connection = mysql.connector.connect(
        host=host_var,
        user=user_var,
        password=password_var,
        database=database_var
    )
    query = f"SELECT * FROM PC_{simulation_id} WHERE agent_id = {agent_id}"
    df = pd.read_sql(query, connection)
    print(df.head(10))
    connection.close()
    return df

def load_simulation_data(simulation_id):
    connection = mysql.connector.connect(
        host=host_var,
        user=user_var,
        password=password_var,
        database=database_var
    )
    table_name = f"PC_{simulation_id}"
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, connection)
    connection.close()
    return df
    # query = f"SELECT * FROM your_table WHERE simulation_id = {simulation_id}"
    # df = pd.read_sql(query, connection)
    # connection.close()
    # return df



########## Database Handling ##########
def load_params(yaml_file):
    with open(yaml_file, 'r') as file:
        params = yaml.safe_load(file)
    return params

def table_exists(conn, table_name):
    cursor = conn.cursor()
    
    # Check if the table exists
    query = "SHOW TABLES LIKE %s"
    
    cursor.execute(query, (table_name,))
    exists = cursor.fetchone()
    
    cursor.close()
    
    return exists is not None

def add_file_to_db(file_number):
    ###############
    agent_data_path = 'FCT_Model/outputs/agent_logger_out_'+ file_number +'.csv'
    theory_data_path = 'FCT_Model/outputs/theory_logger_out_'+ file_number +'.csv'

    agent_df = pd.read_csv(user_path+agent_data_path)

    theory_df = pd.read_csv(user_path+theory_data_path)

    total_df = pd.merge(agent_df, theory_df, left_on=('tick', 'agent_id'), right_on=('tick', 'id'), how='inner')

    total_df.to_csv(user_path+'Data_Processing/outputs/total_'+file_number+'_df.csv')# to be able to see the data.

    ## Database Connection ##
    total_df['simulation_id'] = 'PC_'+file_number

    headers = list(total_df.columns)

    ## Database Connection ##
    total_df['simulation_id'] = 'PC_'+file_number

    headers = list(total_df.columns)
    
    # Connect to the MySQL server
    conn = mysql.connector.connect(
        host=host_var,
        user=user_var,
        password=password_var,
        database=database_var
    )

    cursor = conn.cursor()

    # Check if table already exists
    cursor.execute(f"SHOW TABLES LIKE 'PC_{file_number}'")
    table_found = cursor.fetchone()

    print("conn:", conn)
    print("table_name:", f'PC_{file_number}')


    # If table does not exist, create it
    if not table_found:
        create_table_query = f"CREATE TABLE PC_{file_number} ({', '.join([f'{header} TEXT' for header in headers])})"
        cursor.execute(create_table_query)

    # Check if the simulation already exists in the database
    if table_exists(conn, f'PC_{file_number}'):  # You're now calling the table_exists function
        user_input = input(f'Simulation with ID "PC_{file_number}" already exists. Do you want to add a new run anyway? (y/n): ')
        if user_input.lower() != 'y':
            print('Exiting without adding a new run.')
            conn.close()
            sys.exit()

    # Insert the data from the dataframe into the MySQL database, ignoring duplicate rows
    for index, row in total_df.iterrows():
        values = [str(row[header]) for header in headers]
        insert_query = f"INSERT IGNORE INTO PC_{file_number} ({', '.join(headers)}) VALUES ({', '.join(['%s' for i in range(len(headers))])})"
        cursor.execute(insert_query, values)

    conn.commit()
    conn.close()

def get_total_simulations():
    connection = mysql.connector.connect(
        host=host_var,
        user=user_var,
        password=password_var,
        database=database_var
    )

    query = "SELECT COUNT(TABLE_NAME) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'simulation_data' AND TABLE_NAME LIKE 'PC_%'"
    cursor = connection.cursor()
    cursor.execute(query)
    total_simulations = cursor.fetchone()[0]
    connection.close()
    return total_simulations



########## Graphics Handling ##########
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Simulation Data Visualization"),
    dcc.Dropdown(
        id='simulation-dropdown',
        options=[{'label': f"Simulation {i}", 'value': i} for i in range(1, get_total_simulations() + 1)],
        value=1,
        multi=False,
        clearable=False,
        searchable=True
    ),
    dcc.Dropdown(
        id='agent-dropdown',
        options=[{'label': f"Agent {i}", 'value': i} for i in range(1000)],
        value=0,
        multi=False,
        clearable=False,
        searchable=True
    ),
    dcc.Graph(id='simulation-graph')
])


@app.callback(
    Output('simulation-graph', 'figure'),
    [Input('simulation-dropdown', 'value'),
     Input('agent-dropdown', 'value')]
)
def update_graph(simulation_number, agent_id):
    df = load_simulation_data(simulation_number)
    filtered_df = df[df['agent_id'] == agent_id]

    fig = px.line(filtered_df, x='tick', y='your_value_column', title=f"Agent {agent_id} Data")
    fig.update_xaxes(title="Tick")
    fig.update_yaxes(title="Value")

    return fig




########## Main ##########
if __name__ == "__main__":

    yaml_file = sys.argv[1]
    parameters = load_params(yaml_file)

    #/Users/sebastianozuddas/Programming/Python/FCT_Python/outputs/agent_logger_out.csv
    user_path = '/Users/sebastianozuddas/Programming/Python/FCT_Python/' # set path to your repo
    


    if not all([user_var, password_var]):
        print("Please set the required environment variables: MYSQL_USER, MYSQL_PASSWORD.")
        print(f"User: {user_var}")
        print(f"Password: {password_var}")
        sys.exit(1)

    
    visualize = bool(sys.argv[3])

    if not visualize:
        try:
            file_number = sys.argv[2]
            add_file_to_db(file_number)

        except ValueError:
            print('File number doesn\'t exist, please enter a valid file number\n')
            file_number = input("Enter the file number: ")
            print(f'File number: {file_number}\n')
        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise

    else:
        #visualize the data using the appropriate functions
        match visualize:
            case True:
                print('Visualizing data...\n')
                # visualize_data()
                app.run_server(debug=True)
