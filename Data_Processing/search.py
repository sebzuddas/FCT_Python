import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
import os
import plotly.express as px
import numpy as np
import plotly.graph_objs as go
from typing import List, Dict, Tuple


host_var= '127.0.0.1'
user_var = str(os.environ['MYSQL_USER'])
password_var = str(os.environ['MYSQL_PASSWORD'])
database_var='simulation_data'





def find_ahp_gradients(simulation_id, db_config):
    # Replace these with your database credentials

    ahp_info = []
    harms_dict = {}
    consumption_dict = {}
    data, headers = get_database_tables(simulation_id, db_config)

    for header in headers:
        if not header.startswith('simulation'):
            data[header] = pd.to_numeric(data[header])

    ####### Harms by Deprivation Quintile #######

    total_deaths = get_data_by_dq(data,['death_count'], pivot=True)
    # print(total_deaths)
    total_deaths_melted = total_deaths.reset_index().melt(id_vars='deprivation_quintile', var_name='tick', value_name='value')
    total_deaths_melted = total_deaths_melted.sort_values(['deprivation_quintile', 'tick'])
    # Create a new DataFrame that only includes the rows where 'value' changes within each 'deprivation_quintile'
    total_deaths_changed = total_deaths_melted[total_deaths_melted['value'].diff() != 0]
    # The first row for each 'deprivation_quintile' is removed because it's not a real change
    total_deaths_changed = total_deaths_changed[total_deaths_changed['deprivation_quintile'].eq(total_deaths_changed['deprivation_quintile'].shift())]
    total_deaths_changed['cumulative_value'] = total_deaths_changed.groupby('deprivation_quintile')['value'].cumsum()
    #get the last cumulative sum of deaths over the simulation
    # print(total_deaths_changed)
    total_deaths_sim = total_deaths_changed.groupby('deprivation_quintile')['cumulative_value'].last()
    # print(total_deaths_sim)

    if not total_deaths_sim.empty:
        death_gradient = get_gradient(total_deaths_sim.index, total_deaths_sim.values)
    else:
        # print('total_deaths_sim is empty, cannot calculate gradient')
        death_gradient = 0  # or some other value indicating that the gradient could not be calculated

    # death_gradient = get_gradient(total_deaths_sim.index, total_deaths_sim.values)# death_gradient = filtered_gradients['Death Gradient'].iloc[0]
    # print('death gradient', death_gradient)
    harms_dict['death_final'] = total_deaths_sim
    harms_dict['death_full'] = total_deaths
    
    ####### Adaptation Ratios by Deprivation Quintile #######



    successful_adaptation_data = get_data_by_dq(data, ['successful_adaptiation'], pivot=False)
    unsuccessful_adaptation_data = get_data_by_dq(data, ['unsuccessful_adaptiation'], pivot=False)
    adaptation_data = pd.merge(successful_adaptation_data, unsuccessful_adaptation_data, on=['deprivation_quintile', 'tick'])
    adaptation_data['adaptation_ratio'] = adaptation_data['successful_adaptiation'] / (adaptation_data['successful_adaptiation'] + adaptation_data['unsuccessful_adaptiation'])
    adaptation_data['successful_cumsum'] = adaptation_data.groupby('deprivation_quintile')['successful_adaptiation'].cumsum()
    adaptation_data['unsuccessful_cumsum'] = adaptation_data.groupby('deprivation_quintile')['unsuccessful_adaptiation'].cumsum()
    adaptation_data['adaptation_ratio_cumsum'] = adaptation_data['successful_cumsum'] / (adaptation_data['successful_cumsum'] + adaptation_data['unsuccessful_cumsum'])
    end_simulation_data = adaptation_data.groupby('deprivation_quintile').last().reset_index()
    adaptation_gradient = get_gradient(end_simulation_data['deprivation_quintile'], end_simulation_data['adaptation_ratio_cumsum'])
    
    adaptation_data = data.groupby(['deprivation_quintile', 'tick']).agg({'successful_adaptiation': 'sum', 'unsuccessful_adaptiation': 'sum'}).reset_index()
    adaptation_data['adaptation_ratio'] = adaptation_data['successful_adaptiation'] / (adaptation_data['successful_adaptiation'] + adaptation_data['unsuccessful_adaptiation'])
    adaptation_data = adaptation_data.pivot(index='tick', columns='deprivation_quintile', values='adaptation_ratio')
    adaptation_total = adaptation_data.iloc[:, -1]#Total adaptation ratio by deprivation quintile by the end of the simulation

    harms_dict['adaptation_final'] = adaptation_total
    harms_dict['adaptation_full'] = adaptation_data


    ######### Consumption by Deprivation Quintile #######

    total_consumption = data.groupby(['deprivation_quintile', 'tick']).agg({'mean_weekly_units': 'sum'}).reset_index()
    total_consumption = total_consumption.pivot(index='deprivation_quintile', columns='tick', values='mean_weekly_units')
    mean_consumption_tick = total_consumption.div(200)# average consumption every tick by deprivation quintiles
    mean_consumption_sim = mean_consumption_tick.sum(axis=1) / 520# average consumption throughout the simulation by deprivation quintiles TODO: make dynamic

    
    consumption_dict['consumption_final'] = mean_consumption_sim
    consumption_dict['consumption_full'] = mean_consumption_tick

    ######### Finding the Gradient for Harms ####### (should be positive)
    ### Deaths ###
    harms_dict['death_gradient'] = death_gradient

    ### Successful Adaptations Ratio ###
    harms_dict['adaptation_gradient'] = adaptation_gradient

    ######### Finding the Gradient for Consumption ####### (should be negative)
    consumption_dict['consumption_gradient'] = get_gradient(mean_consumption_sim.index, mean_consumption_sim.values)

    ahp_info.append(harms_dict)
    ahp_info.append(consumption_dict)
    return ahp_info

def get_database_tables(table_number, db_config):
    # Connect to the MySQL database
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Get the table name
    table_name = f"PC_{table_number}"

    # Get column names from the INFORMATION_SCHEMA.COLUMNS table
    column_query = f"""
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{db_config["database"]}' AND TABLE_NAME = '{table_name}'
    """

    cursor.execute(column_query)
    column_names = [column[0] for column in cursor.fetchall()]
    # print(column_names)

    # Join the column names with a comma
    selected_columns = ", ".join(column_names)



    # Query the required data
    query = f'''
    SELECT {selected_columns}
    FROM {table_name}
    '''
    

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    cnx.close()

    # Convert the result to a pandas DataFrame
    return pd.DataFrame(result, columns=column_names), column_names

def get_data_by_dq(df,variables: List[str],pivot=False, pivot_on:int = 0):
    
    agg_dict = {variable: 'sum' for variable in variables}
    # group by 'deprivation_quintile' and 'tick', and aggregate using the variable-aggregation function pairs
    df = df.groupby(['deprivation_quintile', 'tick']).agg(agg_dict).reset_index()

    if pivot:
        df = df.pivot(index='deprivation_quintile', columns='tick', values=variables[pivot_on])#total deaths by deprivation quintile every tick
    
    return df

def get_data_by_agents(df, agents: List):

    pass

def get_gradient(x, y):
    X = np.array(x).reshape(-1, 1)
    Y = np.array(y).reshape(-1, 1)

    reg = LinearRegression()
    reg.fit(X, Y)
    return reg.coef_[0]

def find_number_of_tables(db_config):

    # create a cursor object to execute the query

    cnx = mysql.connector.connect(**db_config)
    mycursor = cnx.cursor()

    # execute the query to count the number of tables
    mycursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'simulation_data'")

    # fetch the result
    result = mycursor.fetchone()[0]

    mycursor.close()
    cnx.close()

    # return the result
    return result

def find_fct():
    pass

def find_ahp(db_config):
    num_tables = find_number_of_tables(db_config)
    # Find the gradient for each simulation
    gradients = []

    print(f"Number of Tables: {num_tables}")



    for simulation_id in range(1, num_tables + 1): 
        try:
            data_dict = find_ahp_gradients(simulation_id, db_config)
            harms_dict = data_dict[0]
            consumption_dict = data_dict[1]
            death_gradient = harms_dict['death_gradient']
            consumption_gradient = consumption_dict['consumption_gradient']
            adaptation_gradient = harms_dict['adaptation_gradient']
            gradients.append((simulation_id, death_gradient, adaptation_gradient, consumption_gradient))
            print(f"Simulation:{simulation_id}\nDeath Gradient:{death_gradient}\nAdaptation Gradient:{adaptation_gradient}\nConsumption Gradient:{consumption_gradient}")
        except ValueError as v:
            print(f"Simulation {simulation_id} failed with error: {v}")
            continue

        
    # Sort the gradients list based on the criteria
    sorted_gradients = sorted(gradients, key=lambda x: (x[1], x[2], -x[3]), reverse=True)
    # Print the sorted list of gradients
    # print("Simulation\tDeath Gradient\tAdaptation Gradient\tConsumption Gradient")
    # for simulation_id, death_gradient, consumption_gradient in sorted_gradients:
    #     print(f"{simulation_id}\t\t{death_gradient}\t\t{adaptation_gradient}\t\t{consumption_gradient}")

    

    column_names = ['Simulation', 'Death Gradient', 'Adaptation Gradient', 'Consumption Gradient']
    sorted_results = pd.DataFrame(sorted_gradients, columns=column_names)
    print(sorted_results)
    # Save the DataFrame to a CSV file
    sorted_results.to_csv('Data_Processing/outputs/gradients/sorted_gradients.csv', index=False)
    return sorted_results


if __name__ == "__main__":

    db_config = {
        'user': user_var,
        'password': password_var,
        'host': host_var,
        'database': database_var,
    }

    find_ahp(db_config)

    exit()
