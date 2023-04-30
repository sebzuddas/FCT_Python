"""
Main file for processing the outputted data from the FCT_Model

"""

import pandas as pd
import plotly.express as px
import yaml
import kaleido

#/Users/sebastianozuddas/Programming/Python/FCT_Python/outputs/tabular_logger_out.csv
user_path = '/Users/sebastianozuddas/Programming/Python/FCT_Python/' # set path to your repo



###############
# record_data_path = '/FCT_Model/outputs/record.csv' # set path to output data
# record_df = pd.read_csv(user_path+record_data_path) # put csv into dataframe 

# record_scatter = px.scatter(record_df)
# record_scatter.show()


def generate_scatter_graph(dataframe, x_axis, y_axis, color, title):

    scatter = px.scatter(dataframe, x=x_axis, y=y_axis, color=color, title=title)
    scatter.show()


def generate_agent_animation(dataframe, x_axis, y_axis, color, title):

    animation = px.scatter(dataframe, x=x_axis, y=y_axis, color=color, title=title, animation_frame='tick')
    animation.show()


def load_params(yaml_file):
    with open(yaml_file, 'r') as file:
        params = yaml.safe_load(file)
    return params


def main():
    ###############
    tabular_data_path = 'FCT_Model/outputs/tabular_logger_out_'+ file_number +'.csv'
    tabular_df = pd.read_csv(user_path+tabular_data_path)
    #print(tabular_df.dtypes)
    #tabular_df['sex'] = tabular_df['sex'].astype(int)
    agent_location_x  = tabular_df['location_x']
    agent_location_y = tabular_df['location_y']
    # tabular_df = tabular_df.drop(columns=['agent_id', 'sex'])
    tabular_df = tabular_df.drop(columns=['sex'])

    graph_extent_x = parameters["board.size"]
    graph_extent_y = parameters["board.size"]

    tabular_animated = px.scatter(tabular_df, x="location_x", y="location_y", animation_frame="tick", animation_group="agent_id",
           size='age', color="deprivation_quintile", hover_name="agent_id",
           log_x=False, range_x=[0,graph_extent_x], range_y=[0,graph_extent_y])

    tabular_animated.show()

    # tabular_animated.write_image("Data_Processing/outputs/Animated_agents.png")

    


    tabular_scatter = px.scatter(tabular_df, x="location_x", y="location_y", 
           size='age', color="deprivation_quintile", hover_name="agent_id",
           log_x=False, range_x=[0,graph_extent_x], range_y=[0,graph_extent_y])
    tabular_scatter.write_image("Data_Processing/outputs/Scatter_agents.png", 'png', width=1920/2, height=1080/2, scale=5)


    

    ###############
    # agent_parameters_data_path = 'FCT_Model/props/agents/agent_props.json'
    # agent_parameters_df = pd.read_json(user_path+agent_parameters_data_path)
    # agent_parameters_df = agent_parameters_df.drop(columns=['agent_id','rank', 'sex', 'agent_type', 'space']) 
    # print(agent_parameters_df)
    # agent_parameters_scatter = px.scatter(agent_parameters_df)
    # agent_parameters_scatter.show()

    # ###############
    # theory_parameters_data_path = 'FCT_Model/props/agents/theory_props.json'
    # theory_parameters_df = pd.read_json(user_path+theory_parameters_data_path)
    # theory_parameters_df = theory_parameters_df.drop(columns=['space']) 
    # print(theory_parameters_df)
    # theory_parameters_scatter = px.scatter(theory_parameters_df)
    # theory_parameters_scatter.show()




if __name__ == "__main__":

    yaml_file = 'FCT_Model/props/model/model.yaml'
    parameters = load_params(yaml_file)
    # parameter_value = parameters['parameter_key']

    try:
        file_number = input("Enter the file number: ")
    except:
        raise ValueError("Please enter a valid file number")
    
    main()