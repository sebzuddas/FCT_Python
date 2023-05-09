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

    ####### Harms by Deprivation Quintile #######

    grouped_data = data.drop(['agent_id', 'successful_adaptiation', 'unsuccessful_adaptiation'], axis=1)
    # grouped_data = grouped_data.groupby(['deprivation_quintile', 'tick']).mean().reset_index()
    grouped_data = data.groupby(['deprivation_quintile', 'tick']).agg({'death_count': 'sum'}).reset_index()
    grouped_data['cumulative_death_count'] = grouped_data.groupby('deprivation_quintile')['death_count'].cumsum()
    grouped_data = grouped_data.pivot(index='tick', columns='deprivation_quintile', values='cumulative_death_count')

    # fig = px.line(grouped_data, x=grouped_data.index, y=grouped_data.columns)
    # fig.show()
    # print(grouped_data)

    total_deaths = data.groupby(['deprivation_quintile', 'tick']).agg({'death_count': 'sum'}).reset_index()
    total_deaths['cumulative_death_count'] = total_deaths.groupby('deprivation_quintile')['death_count'].cumsum()
    total_deaths = total_deaths.pivot(index='deprivation_quintile', columns='tick', values='death_count')

    # fig2 = px.bar(total_deaths, x=total_deaths.index, y=total_deaths.columns.max())
    # fig2.update_layout(yaxis_title='Total Deaths', xaxis_title='Deprivation Quintile', title='Total Deaths per Deprivation Quintile', font=dict(
    #     family='serif',
    #     size=18,
    #     color='black'
    # ))
    # fig2.show()

    ######### Consumption by Deprivation Quintile #######

    total_consumption = data.groupby(['deprivation_quintile', 'tick']).agg({'mean_weekly_units': 'sum'}).reset_index()
    total_consumption = total_consumption.pivot(index='deprivation_quintile', columns='tick', values='mean_weekly_units')
    mean_consumption_tick = total_consumption.div(200)

    print(mean_consumption_tick)

    # mean consumption simulation
    mean_consumption_sim = mean_consumption_tick.sum(axis=1) / 1040
    print(mean_consumption_sim)
    
    # total_consumption['cumulative_consumption'] = total_consumption.groupby('deprivation_quintile')['mean_weekly_units'].cumsum()







    
    # print(total_consumption.columns.max())

    exit()

    fig3 = px.bar(total_consumption, x=total_consumption.index, y=total_consumption.columns.max())

    fig3.update_layout(yaxis_title='Consumption', xaxis_title='Deprivation Quintile', title='Total Consumption per Deprivation Quintile', font=dict(
        family='serif',
        size=18,
        color='black'
    ))

    fig3.show()



    # print(total_deaths)
    exit()
    
    #starting with finding averages per year:

    yearly_data = pd.DataFrame(result, columns=columns)
    yearly_data = yearly_data.groupby(['deprivation_quintile', 'tick'])


    print(yearly_data.head(10))
    exit()  











    # Group the data by deprivation_quintile and tick
    grouped_data = data.groupby(['deprivation_quintile', 'tick']).sum().reset_index()

    for quintile in grouped_data['deprivation_quintile'].unique():
        quintile_data = grouped_data[grouped_data['deprivation_quintile'] == quintile]
        X = quintile_data['tick'].values.reshape(-1, 1)
        y = quintile_data['death_count'].values

        model = LinearRegression()
        model.fit(X, y)

        gradient = model.coef_[0]




        ticks = np.linspace(grouped_data['tick'].min(), grouped_data['tick'].max(), num=100)
        predicted_counts = model.predict(ticks.reshape(-1, 1))

        # # add the predicted values to the DataFrame
        predictions = predictions.append(pd.DataFrame({'deprivation_quintile': [quintile]*len(ticks),
                                                        'tick': ticks,
                                                        'predicted_death_count': predicted_counts}))


        # create a line plot using Plotly Express
    fig = px.line(predictions, x='tick', y='predicted_death_count', color='deprivation_quintile')

    
    # Close the database connection
    cursor.close()
    cnx.close()
    fig.show()
    exit()


    return gradient


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
    
        test = find_ahp(simulation_id, db_config)
        print(f"Simulation:{simulation_id}\nHarm Gradient:{test}")



    # Calculate the gradient of harms/deprivation_quintile for each simulation
    exit()
    
    



    gradients.append((quintile, gradient))
    # Filter simulations with a negative gradient and sort by the largest negative gradient
    negative_gradients = sorted([(q, g) for q, g in gradients if g < 0], key=lambda x: x[1])

    print("Quintile\tGradient")
    for quintile, gradient in negative_gradients:
        print(f"{quintile}\t\t{gradient}")
    
    print(f"{gradients}")
    exit(0)
