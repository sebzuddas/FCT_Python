"""
Main file for processing the outputted data from the FCT_Model
change
test_change2
"""

import pandas as pd
import plotly.express as px

user_path = '/Users/sebastianozuddas/Programming/Python/FCT_Python' # set path to your repo
data_path = '/FCT_Model/outputs/record.csv' # set path to output data
df = pd.read_csv(user_path+data_path) # put csv into dataframe 
print(df)

scatter = px.scatter(df)

scatter.show()