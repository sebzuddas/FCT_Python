"""
Main file for managing the different experiments that will be run on the FCT_Model

Types of experiments:
#TODO: create some experiments
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

### Variable Declaration
sample_number = 100 # number of experiments

standard_props_file_location = "/Users/sebastianozuddas/Programming/Python/FCT_Python/FCT_Model/props/model/standard.yaml"


# make a python main function for the experiment generator
def main():

    create_yaml_file(experiment_number, standard_props_file_location)

### Functions
#create a function for the previous loop to create a new yaml file for each sample.
def create_yaml_file(sample_number, example_file, target_folder='/Users/sebastianozuddas/Programming/Python/FCT_Python/FCT_Model/props/model/test_parameters'):
    
    # Create the target folder if it does not exist
    os.makedirs(target_folder, exist_ok=True)

    with open(example_file) as f:
        props_file = yaml.safe_load(f)
    
    # Define keys of the parameters you want to modify
    keys_to_modify = ['successful.adaptation.cost', 'unsuccessful.adaptation.cost', 'successful.adaptation.knowlege.benefit']

    # Define the bounds for each parameter you want to modify
    bounds = [(1, 30), (1, 30), (10, 20)]

    engine = LatinHypercube(len(keys_to_modify))
    sample = engine.random(sample_number)

    for i in range(len(sample)):
        for j, key in enumerate(keys_to_modify):
            # Scale and shift the LHS sample according to the parameter bounds
            value = sample[i][j] * (bounds[j][1] - bounds[j][0]) + bounds[j][0]
            
            # Round the value to the nearest integer
            value = round(value)

            # Update the parameter with the modified value
            props_file[key] = value
        
        with open(os.path.join(target_folder, f'test_{i+1}.yaml'), 'w') as f:
            yaml.dump(props_file, f)





def generate_probability(probability_type):
    #create a function that takes in a probability type and returns a random probability based on the type requested
    if probability_type == 'uniform':
        return random.uniform(0,1)
    elif probability_type == 'normal':
        return random.normal(0,1)
    elif probability_type == 'lognormal':
        return random.lognormal(0,1)
    elif probability_type == 'exponential':
        return random.exponential(1)
    elif probability_type == 'gamma':
        return random.gamma(1,1)
    elif probability_type == 'beta':
        return random.beta(1,1)
    elif probability_type == 'binomial':
        return random.binomial(1,0.5)
    elif probability_type == 'poisson':
        return random.poisson(1)
    elif probability_type == 'geometric':
        return random.geometric(0.5)
    elif probability_type == 'negative_binomial':
        return random.negative_binomial(1,0.5)
    elif probability_type == 'logistic':
        return random.logistic(0,1)
    elif probability_type == 'logseries':
        return random.logseries(0.5)
    elif probability_type == 'chisquare':
        return random.chisquare(1)

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

