import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import os
import mysql.connector
import sys


host_var='127.0.0.1'
user_var = str(os.environ['MYSQL_USER'])
password_var = str(os.environ['MYSQL_PASSWORD'])
database_var='simulation_data'




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




def main():
    pass

def display_network(df):
    
    pass

def display_harms(df):
    pass

def animate_simulation(sim_number):
    pass

if __name__ == "__main__":

    display_type = sys.argv[1]

    if display_type == 'network':
        display_network()
    elif display_type == 'harms':
        display_harms()
    elif display_type == 'animate':
        animate_simulation()
    else:
        print('Invalid display type. Please enter either "network", "harms" or "animate"')
        sys.exit()

    main()