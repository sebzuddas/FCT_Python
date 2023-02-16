"""
Main file for managing the different experiments that will be run on the FCT_Model

Types of experiments:
#TODO: create some experiments
1. LHS
2. Different social networks 
3. Inclusion of another social theory with the mediator class?
4. Testing and verifying FCT
    4.1 Include interesting distributions wrt FCT such as power, money, prestige

#TODO make the props file take input 

Sebastiano Zuddas
"""

### Imports
from scipy.stats.qmc import LatinHypercube
import yaml
import json


### Variable Declaration
dimensions = 2
sample_number = 100


#TODO make the LatinHypercube dimensions based on the properties file
#TODO extend the LatinHypercube to further params


props_file_location = "/Users/sebastianozuddas/Programming/Python/FCT_Python/FCT_Model/props/test.yaml"

with open(props_file_location) as f:
    props_file = yaml.safe_load(f)
    

engine = LatinHypercube(len(props_file))
sample = engine.random(sample_number)

#TODO generate a set of tests determined by the sample number. 
#TODO Ensure that integers are there when needed. 


for i in len(sample):# over '100' samples
    for j in len(sample[1]):# use the 5 parameters
        """
        with open(props_file_location, "w") as f:
        yaml.dump(props_file + str(i), f)

        #TODO create a dict to dump in yaml file
        """


# for props in props_file:
#     props[props]=sample[1][props]

# print(engine)
# print(sample[1][1])
# print(len(sample[1]))
# print(len(sample))



with open(props_file_location, "w") as f:
    yaml.dump(props_file, f)



#for param in props_file:# loop through all the parameters
#    param["random.seed"]=2

#props_file['random.seed'] = 2
    #yaml.dump(props_file, f)



#TODO Write to the props file and change some of the parameters


print(props_file)