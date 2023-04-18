"""
Main file for processing the outputted data from the FCT_Model

"""

import pandas as pd
import plotly.express as px
import repast4py

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



def main():
    ###############
    tabular_data_path = 'FCT_Model/outputs/tabular_logger_out_4.csv'
    tabular_df = pd.read_csv(user_path+tabular_data_path)
    #print(tabular_df.dtypes)
    #tabular_df['sex'] = tabular_df['sex'].astype(int)
    agent_location_x  = tabular_df['location_x']
    agent_location_y = tabular_df['location_y']
    # tabular_df = tabular_df.drop(columns=['agent_id', 'sex'])
    tabular_df = tabular_df.drop(columns=['sex'])

    graph_extent_x = 50
    graph_extent_y = 50

    tabular_animated = px.scatter(tabular_df, x="location_x", y="location_y", animation_frame="tick", animation_group="agent_id",
           size='age', color="deprivation_quintile", hover_name="deprivation_quintile",
           log_x=False, range_x=[0,graph_extent_x], range_y=[0,graph_extent_y])
    

    # tabular_scatter = px.scatter(tabular_df)
    # tabular_scatter.show()

    tabular_animated.show()

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
    # parser = repast4py.parameters.create_args_parser()
    # args = parser.parse_args()
    # params = repast4py.parameters.init_params(args.parameters_file, args.parameters)
    main()