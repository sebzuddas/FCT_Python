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

