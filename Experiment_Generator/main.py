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


### Variable Declaration
sample_number = 100 # number of experiments

props_file_location = "/Users/sebastianozuddas/Programming/Python/FCT_Python/FCT_Model/props/test.yaml"


# make a python main function for the experiment generator
def main():
    experiments.create_yaml_file(sample_number, props_file_location, target_folder='FCT_Model/props/test_LHS')


    
    if __name__ == "__main__":
    main()

