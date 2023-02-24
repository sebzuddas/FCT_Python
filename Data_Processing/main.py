"""
Main file for processing the outputted data from the FCT_Model

"""

import pandas as pd
import plotly.express as px

user_path = '/Users/sebastianozuddas/Programming/Python/FCT_Python' # set path to your repo


###############
# record_data_path = '/FCT_Model/outputs/record.csv' # set path to output data
# record_df = pd.read_csv(user_path+record_data_path) # put csv into dataframe 

# record_scatter = px.scatter(record_df)
# record_scatter.show()



###############
tabular_data_path = '/outputs/tabular_logger_out.csv'
tabular_df = pd.read_csv(user_path+tabular_data_path)
#print(tabular_df.dtypes)
#tabular_df['sex'] = tabular_df['sex'].astype(int)
tabular_df = tabular_df.drop(columns=['agent_id', 'sex'])

tabular_scatter = px.scatter(tabular_df)
tabular_scatter.show()

    

    

#/Users/sebastianozuddas/Programming/Python/FCT_Python/outputs/tabular_logger_out.csv