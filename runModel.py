#!/usr/bin/env python3

#runModel.py is a python-based command line intergface for running FCT_Model/main.py


# Path: FCT_Model/main.py

# Compare this snippet from FCT_Model/main.py:
# """
# Main file for running the FCT_Model
#
# Sebastiano Zuddas
# """

import sys
import os
import click
import colorama
import emojis

colorama.init()

@click.group()
def model():
    pass

@model.command()
#@click.argument('-r')
@click.option('-r/--run', default=False, help='Run the model in its default state')
def run(**kwargs):
    print(emojis.encode(colorama.Fore.BLUE+"Attempting to run the model :confused: \n"))
    colorama.Fore.RESET  
    

    try:
        os.system('python3 FCT_Model/main.py FCT_Model/props/model.yaml')
        print(emojis.encode(colorama.Fore.GREEN+"Model run successfully! :smirk: \n"))
        
    except(KeyboardInterrupt):
        print(emojis.encode(colorama.Fore.RED+"Error: unable to run the model :sad: \n"))
    
    except(EOFError):
        print(emojis.encode(colorama.Fore.RED+"Error: unable to run the model :sad: \n"))

    except(ImportError):
        print(emojis.encode(colorama.Fore.RED+"Error: unable to run the model :sad: \n"))
    
    except(FileNotFoundError):
        print(emojis.encode(colorama.Fore.RED+"Error: unable to run the model :sad: \n"))


    

    

@model.command()
@click.option('-p/--props', default=False, help='Run the model with the specified properties file')
def props(**kwargs):
    print(emojis.encode(colorama.Fore.BLUE+"Running the model with the specified properties file {0} :cow: ".format(kwargs['p'])))
    pass



# @greet.command()
# def hello(**kwargs):
#     pass

# @greet.command()
# @click.argument('name')
# @click.option('--count', default=1, help='Number of greetings.')
# def goodbye(**kwargs):
#     print("Goodbye, {0}".format(kwargs['name']))

if __name__ == "__main__":
    model()
