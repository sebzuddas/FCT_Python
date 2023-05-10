import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
import os
import plotly.express as px
import numpy as np
import plotly.graph_objs as go


host_var= '127.0.0.1'
user_var = str(os.environ['MYSQL_USER'])
password_var = str(os.environ['MYSQL_PASSWORD'])
database_var='simulation_data'





def find_ahp(simulation_id, db_config):
    # Replace these with your database credentials

    ahp_info = []
    harms_dict = {}
    consumption_dict = {}
    

    # Connect to the MySQL database
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Query the required data
    query = f'''
    SELECT tick, agent_id, deprivation_quintile, death_count, mean_weekly_units, successful_adaptiation, unsuccessful_adaptiation
    FROM PC_{simulation_id}
    '''

    cursor.execute(query)
    result = cursor.fetchall()

    # Convert the result to a pandas DataFrame
    columns = ['tick', 'agent_id', 'deprivation_quintile', 'death_count', 'mean_weekly_units', 'successful_adaptiation', 'unsuccessful_adaptiation']
    data = pd.DataFrame(result, columns=columns)
    data['tick'] = pd.to_numeric(data['tick'])
    data['death_count'] = pd.to_numeric(data['death_count'])
    data['mean_weekly_units'] = pd.to_numeric(data['mean_weekly_units'])
    data['successful_adaptiation'] = pd.to_numeric(data['successful_adaptiation'])
    data['unsuccessful_adaptiation'] = pd.to_numeric(data['unsuccessful_adaptiation'])#Currently NAN

    ####### Harms by Deprivation Quintile #######

    total_deaths = data.groupby(['deprivation_quintile', 'tick']).agg({'death_count': 'sum'}).reset_index()
    total_deaths = total_deaths.pivot(index='deprivation_quintile', columns='tick', values='death_count')#total deaths by deprivation quintile every tick
    tot_deaths_sim = total_deaths.iloc[:, -1]#Total deaths by deprivation quintile by the end of the simulation

    harms_dict['death_final'] = tot_deaths_sim
    harms_dict['death_full'] = total_deaths
    
    ####### Adaptation Ratios by Deprivation Quintile #######

    
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
    mean_consumption_sim = mean_consumption_tick.sum(axis=1) / 1040# average consumption throughout the simulation by deprivation quintiles
    
    consumption_dict['consumption_final'] = mean_consumption_sim
    consumption_dict['consumption_full'] = mean_consumption_tick

    ######### Finding the Gradient for Harms ####### (should be positive)
    ### Deaths ###

    X1 = np.array(tot_deaths_sim.index).reshape(-1, 1)
    y1 = np.array(tot_deaths_sim.values).reshape(-1, 1)
    
    deaths_gradient = get_gradient(X1, y1)
    harms_dict['death_gradient'] = deaths_gradient

    ### Successful Adaptations Ratio ###
    
    X2 = np.array(adaptation_total.index).reshape(-1, 1)
    y2 = np.array(adaptation_total.values).reshape(-1, 1)
    adaptation_gradient = get_gradient(X2, y2)
    harms_dict['adaptation_gradient'] = adaptation_gradient



    ######### Finding the Gradient for Consumption ####### (should be negative)
    X3 = np.array(mean_consumption_sim.index).reshape(-1, 1)
    y3 = np.array(mean_consumption_sim.values).reshape(-1, 1)
    consumption_gradient = get_gradient(X3, y3)
    consumption_dict['consumption_gradient'] = consumption_gradient

    ahp_info.append(harms_dict)
    ahp_info.append(consumption_dict)
    cursor.close()
    cnx.close()

    return ahp_info


def get_data_by_dq(df, variable):
    pass

def get_gradient(x, y):
    reg = LinearRegression()
    reg.fit(x, y)
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


if __name__ == "__main__":

    db_config = {
        'user': user_var,
        'password': password_var,
        'host': host_var,
        'database': database_var,
    }

    num_tables = find_number_of_tables(db_config)
    # Find the gradient for each simulation
    gradients = []

    print(f"Number of Tables: {num_tables}")

    for simulation_id in range(1, num_tables + 1): 
    
        data_dict = find_ahp(simulation_id, db_config)
        harms_dict = data_dict[0]
        consumption_dict = data_dict[1]
        death_gradient = harms_dict['death_gradient']
        consumption_gradient = consumption_dict['consumption_gradient']
        adaptation_gradient = harms_dict['adaptation_gradient']
        gradients.append((simulation_id, death_gradient, adaptation_gradient, consumption_gradient))
        print(f"Simulation:{simulation_id}\nDeath Gradient:{death_gradient}\nAdaptation Gradient:{adaptation_gradient}\nConsumption Gradient:{consumption_gradient}")
    

    
    
    # Sort the gradients list based on the criteria
    sorted_gradients = sorted(gradients, key=lambda x: (x[1], -x[2]), reverse=True)
    # Print the sorted list of gradients
    print("Simulation\tDeath Gradient\tAdaptation Gradient\tConsumption Gradient")
    for simulation_id, death_gradient, consumption_gradient in sorted_gradients:
        print(f"{simulation_id}\t\t{death_gradient}\t\t{adaptation_gradient}\t\t{consumption_gradient}")

    

    column_names = ['Simulation', 'Death Gradient', 'Adaptation Gradient', 'Consumption Gradient']
    sorted_results = pd.DataFrame(sorted_gradients, columns=column_names)
    print(sorted_results)

    # Save the DataFrame to a CSV file
    sorted_results.to_csv('Data_Processing/outputs/gradients/sorted_gradients.csv', index=False)

    exit()
