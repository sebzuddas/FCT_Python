"""
Main file for managing the different experiments that will be run on the FCT_Model

Types of experiments:
#TODO: create some experiments
1. LHS
2. Different social networks 
3. Inclusion of another social theory with the mediator class?
4. Testing and verifying FCT



Sebastiano Zuddas
"""

from scipy.stats.qmc import LatinHypercube
import yaml


dimensions = 2
sample_number = 100
engine = LatinHypercube(dimensions)
sample = engine.random(sample_number)



props_file_location = "/Users/sebastianozuddas/Programming/Python/FCT_Python/FCT_Model/props/test.yaml"


with open(props_file_location) as f:
    props_file = yaml.safe_load(f)










print(props_file)