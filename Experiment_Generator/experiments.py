from scipy.stats.qmc import LatinHypercube
from numpy import random
import yaml


### Functions
#create a function for the previous loop to create a new yaml file for each sample.
def create_yaml_file(sample_number, props_file_location, target_folder):
    with open(props_file_location) as f:
        props_file = yaml.safe_load(f)

    engine = LatinHypercube(len(props_file))
    sample = engine.random(sample_number)

    props_dict_key_list = list(props_file) #dictionary key to index the props file. 
    props_dict_vals_list = list(props_file.values())
    props_dict_reference = list(props_file.values())
    props_dict_vals_list[0] = sample[0][0]
    # print(props_dict_vals_list)
    # print(props_dict_list[0])
    # print(props_dict_list)

    for i in range(len(sample)):# over '100' samples
        # print(sample)
        # print(test_num)
        for j in range(len(sample[i])):
            props_dict_vals_list[j] = int(sample[i][j]*10)*props_dict_reference[j]
            with open(target_folder+'/test_'+str(i)+'.yaml', 'w') as f:
                yaml.dump(dict(zip(props_dict_key_list, props_dict_vals_list)), f)

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

        

#TODO: create a function that generates a distribution for the theory class
# def generate_theory_distributions(type):
#     experiment = type
#     match experiment:
#         case 1:
#             pass
    