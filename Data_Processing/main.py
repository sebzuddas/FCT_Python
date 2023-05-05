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

#/Users/sebastianozuddas/Programming/Python/FCT_Python/outputs/agent_logger_out.csv
user_path = '/Users/sebastianozuddas/Programming/Python/FCT_Python/' # set path to your repo
app = dash.Dash()


def load_params(yaml_file):
    with open(yaml_file, 'r') as file:
        params = yaml.safe_load(file)
    return params



# def read_data_from_db(simulation_id):




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




    add_file_to_db(file_number, parameters)



    



