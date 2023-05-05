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
import sqlite3
import requests

#/Users/sebastianozuddas/Programming/Python/FCT_Python/outputs/agent_logger_out.csv
user_path = '/Users/sebastianozuddas/Programming/Python/FCT_Python/' # set path to your repo


def load_params(yaml_file):
    with open(yaml_file, 'r') as file:
        params = yaml.safe_load(file)
    return params


def simulation_exists(conn, simulation_id):
    cursor = conn.execute(f"SELECT COUNT(*) FROM my_table WHERE simulation_id='{simulation_id}'")
    count = cursor.fetchone()[0]
    return count > 0

def send_database_to_server(file_number, server_url='http://178.79.134.28:5000/upload_simulation'):
    simulation_data_path = 'Data_Processing/outputs/simulations.db'
    conn = sqlite3.connect(user_path+simulation_data_path)


    if file_number == 0:#send everything
        pass

def send_csv_to_server(file_number, server_url='http://178.79.134.28:5000/upload_simulation'):
    summarised_data_path = 'Data_Processing/outputs/total_'+ file_number +'_df.csv'
    summarised_df = pd.read_csv(user_path+summarised_data_path)

    
    if file_number == 0:#send everything
        pass

    pass

def send_json_to_server(file_number, server_url='http://178.79.134.28:5000/upload_simulation'):
    summarised_data_path = 'Data_Processing/outputs/total_'+ file_number +'_df.csv'
    summarised_df = pd.read_csv(user_path+summarised_data_path)

    
    json_data = {
        "table_name": table_name,
        "headers": headers,
        "data": data
    }

    # Send the JSON data to the server using the API
    response = requests.post(server_url, json=json_data)

    if response.status_code == 200:
        print('Simulation data sent successfully.')
    else:
        print(f'Error sending simulation data. Status code: {response.status_code}')
    
    if file_number == 0:#send everything
        pass

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
    conn = sqlite3.connect('Data_Processing/outputs/simulations.db')

    # Check if table already exists
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='my_table'")
    table_exists = cursor.fetchone()

    # If table does not exist, create it
    if not table_exists:
        create_table_query = f"CREATE TABLE my_table ({','.join(headers)})"
        conn.execute(create_table_query)


        # Check if the simulation already exists in the database
    if simulation_exists(conn, 'PC_'+file_number):
        user_input = input(f'Simulation with ID "PC_{file_number}" already exists. Do you want to add a new run anyway? (y/n): ')
        if user_input.lower() != 'y':
            print('Exiting without adding a new run.')
            conn.close()
            sys.exit()

    # Insert the data from the dataframe into the SQLite database, ignoring duplicate rows
    for index, row in total_df.iterrows():
        values = [str(row[header]) for header in headers]
        insert_query = f"INSERT OR IGNORE INTO my_table ({','.join(headers)}) VALUES ({','.join(['?' for i in range(len(headers))])})"
        conn.execute(insert_query, values)

    conn.commit()
    conn.close()





if __name__ == "__main__":
    
    

    yaml_file = sys.argv[1]
    parameters = load_params(yaml_file)
    

    try:
        file_number = sys.argv[2]
    except ValueError:
        print('File number doesn\'t exist, please enter a valid file number\n')
        file_number = input("Enter the file number: ")
        print(f'File number: {file_number}\n')
    except:
        print('Unexpected error:', sys.exc_info()[0])
        raise

    data_type = sys.argv[3]


    match data_type:
        case 0:
            print(f'Send: {file_number}! Sending simulation {file_number} database to server...\n')
            send_database_to_server(file_number)
        case 1:
            print(f'Send: {file_number}! Sending simulation {file_number} database to server...\n')
            send_csv_to_server(file_number)
        case 2:
            print(f'Send: {file_number}! Sending simulation {file_number} database to server...\n')
            send_json_to_server(file_number)
        case _:
            raise ValueError(f'Invalid data type: {data_type}. Valid data types are 0, 1, or 2 for database, csv, or json, respectively.')
        

    # try:
    #     print(f'Send: {send}! Sending simulation {file_number} database to server...\n')

    #     table_name = 'my_table'
    #     headers = list(total_df.columns)
    #     data = [row.to_dict() for _, row in total_df.iterrows()]




    # except IndexError:
    #     send = False


        


    add_file_to_db(file_number, parameters)







