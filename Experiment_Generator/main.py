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

### Variable Declaration
sample_number = 100 # number of experiments

props_file_location = "/Users/sebastianozuddas/Programming/Python/FCT_Python/FCT_Model/props/test.yaml"

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
        with open('FCT_Model/props/test_LHS/test_'+str(i)+'.yaml', 'w') as f:
            yaml.dump(dict(zip(props_dict_key_list, props_dict_vals_list)), f)