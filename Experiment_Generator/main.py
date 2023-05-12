"""
Main file for managing the different experiments that will be run on the FCT_Model

Types of experiments:
1. LHS
2. Different social networks 
3. Inclusion of another social theory with the mediator class?
4. Testing and verifying FCT
    4.1 Include interesting distributions wrt FCT such as power, money, prestige

#TODO Ensure that integers are there when needed. 
#TODO counts.of.agents must be less than board.size
#TODO extend the LatinHypercube to further params
#TODO Make LHS output reasonable bounds

Sebastiano Zuddas
"""

### Imports
from scipy.stats.qmc import LatinHypercube
import yaml
import experiments
import random
import sys
import os
import numpy as np

### Variable Declaration
sample_number = 100 # number of experiments
standard_props_file_location = "/Users/sebastianozuddas/Programming/Python/FCT_Python/FCT_Model/props/model/standard.yaml"

# make a python main function for the experiment generator
def main():

    create_yaml_file(experiment_number, standard_props_file_location)

### Functions
#create a function for the previous loop to create a new yaml file for each sample.
def create_yaml_file(sample_number, example_file, target_folder='/Users/sebastianozuddas/Programming/Python/FCT_Python/FCT_Model/props/model/test_parameters'):
    

    def convert_value(value, key):
        if key in decimal_keys:
            return round(value, 6)  # You can change the number of decimals as needed
        return int(round(value))
    
    # Create the target folder if it does not exist
    os.makedirs(target_folder, exist_ok=True)

    with open(example_file) as f:
        props_file = yaml.safe_load(f)

    # agent_logger: FCT_Model/outputs/agent_logger_out.csv
    # agent_props_file: FCT_Model/props/agents/agent_props.json
    # area_file: FCT_Model/props/area/DQ_areas.csv
    # board_props_file: FCT_Model/props/area/DQ_areas.csv
    # network_file: FCT_Model/props/network/graph.txt
    # network_file_updated: FCT_Model/props/network/graph_updated.txt
    # theory_logger: FCT_Model/outputs/theory_logger_out.csv
    # theory_props_file: FCT_Model/props/agents/theory_props.json

    keys_with_string_values = ['agent.logger',
                               'agent.props.file', 
                               'area.file', 
                               'board.props.file', 
                               'network.file', 
                               'network.file.updated', 
                               'theory.logger', 
                               'theory.props.file']

    # Define keys of the parameters you want to modify
    keys_to_modify = ['min.age', 
                      'max.age', 
                      'risk.threshold', 
                      'successful.adaptation.cost', 
                      'unsuccessful.adaptation.cost', 
                      'successful.adaptation.knowlege.benefit', 
                      'communicator.max.reach', 
                      'beta.modifier.male', 
                      'beta.modifier.female', 
                      'knowledge.gain',
                      'resource.depletion',
                      'theory.distribution.type', 
                      'communication.success', 
                      'drink.distribution.type']

    # Define the bounds for each parameter you want to modify
    bounds = [(18, 56), 
              (56, 95), 
              (0, 1), 
              (1, 3), 
              (1, 3), 
              (1, 2), 
              (1, 1000), 
              (0.001, 0.005),
              (0.0005, 0.0015), 
              (0.5, 1),
              (0, 1),
              (1, 3), 
              (0, 1), 
              (1, 2)
              ]

    # Define the keys you want to have as decimals
    decimal_keys = ['risk.threshold', 
                    'successful.adaptation.cost', 
                    'unsuccessful.adaptation.cost', 
                    'successful.adaptation.knowlege.benefit', 
                    'beta.modifier.male', 
                    'beta.modifier.female', 
                    'knowledge.gain', 
                    'resource.depletion', 
                    'communication.success']

    engine = LatinHypercube(len(keys_to_modify))
    sample = engine.random(sample_number)

    for i in range(len(sample)):
        for j, key in enumerate(keys_to_modify):
            if key not in keys_with_string_values:
                # Scale and shift the LHS sample according to the parameter bounds
                value = sample[i][j] * (bounds[j][1] - bounds[j][0]) + bounds[j][0]

                # Update the parameter with the converted value
                props_file[key] = convert_value(value, key)
                # print(f'Updating {key}: {value}')  # Debug print

        # Convert numpy values to native Python data types
        cleaned_props_file = numpy_to_python(props_file)
        # print(f'Cleaned props file: {cleaned_props_file}')  # Debug print

        # Save the cleaned YAML file without numpy tags
        yaml_filename = os.path.join(target_folder, f'test_{i+1}.yaml')
        yaml_dump(cleaned_props_file, yaml_filename)
        # print(f'Saved YAML file: {yaml_filename}')  # Debug print

        # Read the saved YAML file to check the contents
        with open(yaml_filename, 'r') as yaml_file:
            yaml_contents = yaml.safe_load(yaml_file)
            print(f'YAML contents: {yaml_contents}')  # Debug print



def numpy_float_representer(dumper, value):
    return dumper.represent_float(value)


def yaml_dump(data, file_name):
    with open(file_name, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def numpy_to_python(data):
    if isinstance(data, dict):
        cleaned_data = {}
        for k, v in data.items():
            cleaned_key = k.rstrip(' :')
            cleaned_data[cleaned_key] = numpy_to_python(v)
        return cleaned_data
    elif isinstance(data, list):
        return [numpy_to_python(v) for v in data]
    elif isinstance(data, np.generic):
        return data.item()
    else:
        return data




def generate_agent_distributions(type):

    dict = {"age": [], "drinking_status": []}


    experiment = type
    match experiment:
       
        case 1:# normal population, low drinking status
            dict["age"] = [18, 80]
            dict["drinking_status"] = [0, 2]
            return dict
        
        case 2:# normal population, high drinking status
            dict["age"] = [18, 80]
            dict["drinking_status"] = [2, 4]
            return dict
                
        case 3:# low population, high drinking status
            dict["age"] = [18, 40]
            dict["drinking_status"] = [2, 4]
            return dict
        
        case 4:# low population, normal drinking status
            dict["age"] = [18, 40]
            dict["drinking_status"] = [0, 4]
            return dict
            
        case 5:# low population, low drinking status
            dict["age"] = [18, 40]
            dict["drinking_status"] = [0, 2]
            return dict
        
        case 6:# high population, high drinking status
            dict["age"] = [40, 80]
            dict["drinking_status"] = [2, 4]
            return dict
        case 7:# high population, normal drinking status
            dict["age"] = [40, 80]
            dict["drinking_status"] = [0, 4]
            return dict
            
        case 8:# high population, low drinking status
            dict["age"] = [40, 40]
            dict["drinking_status"] = [0, 2]
            return dict

        case _:# normal population, normal drinking status
            dict["age"] = [18, 80]
            dict["drinking_status"] = [0, 4]
            return dict
        
def generate_theory_distributions(type):

    dict = {"mean_weekly_units": [], "education": [], "personal_wealth": []}

    match type:
       
       #changing weekly units
        case 1:# high consumption, normal education, normal wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 2:# normal consumption, normal education, high wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 3:# normal consumption, high education, normal wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 4:# normal consumption, normal education, low wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 5:# normal consumption, low education, normal wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["n"]
            return dict
        case 6:# low consumption, normal education, normal wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 7:# normal consumption, high education, high wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 8:# high consumption, normal education, high wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 9:# high consumption, high education, normal wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 10:# normal consumption, high education, low wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 11:# normal consumption, low education, high wealth inequality
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["p"]
            return dict
        case 12:# high consumption, normal education, low wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 13:# high consumption, low education, normal wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["n"]
            return dict
        case 14:# low consumption, normal education, high wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 15:# low consumption, high education, normal wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["n"]
            return dict
        case 16:# high consumption, low education, low wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["u"]
            return dict
        case 17:# low consumption, high education, low wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 18:# low consumption, low education, high wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["p"]
            return dict
        case 19:# high consumption, high education, high wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 20:# high consumption, high education, low wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 21:# high consumption, low education, high wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["p"]
            return dict
        case 22:# low consumption, high education, high wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["p"]
            return dict
        case 23:# high consumption, low education, low wealth inequality
            dict["mean_weekly_units"] = [600, 1300]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["u"]
            return dict
        case 24:# low consumption, high education, low wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [2, 3]
            dict["personal_wealth"] = ["u"]
            return dict
        case 25:# low consumption, low education, high wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["p"]
            return dict
        case 26:# low consumption, low education, low wealth inequality
            dict["mean_weekly_units"] = [0, 600]
            dict["education"] = [1, 2]
            dict["personal_wealth"] = ["u"]
            return dict
        case _:# normal drinking habits, normal education levels, normal wealth distributions
            dict["mean_weekly_units"] = [0, 1300]
            dict["education"] = [1, 3]
            dict["personal_wealth"] = ["n"] #uniform wealth distribution
            return dict

    
if __name__ == "__main__":
    
    experiment_number = int(sys.argv[1])
    

    main()

