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
import subprocess

colorama.init()

@click.group()
def model():
    pass

@model.command()
#@click.argument('-r')
@click.option('-r', default=False, help='Run the model in its default state')
def run(**kwargs):
    print(emojis.encode(colorama.Fore.BLUE+"Attempting to run the model :confused: \n"))
    colorama.Fore.RESET  
 
    try:
        subprocess.run(["python3" ,"FCT_Model/main.py", "FCT_Model/props/model.yaml"], check=True)
        print(emojis.encode(colorama.Fore.GREEN+"Model run successfully! :smirk: \n"))
        
    except(KeyboardInterrupt):
        print(emojis.encode(colorama.Fore.RED+"You stopped the model running! :unamused: \n "))
    
    except subprocess.CalledProcessError as e:
        print(emojis.encode(colorama.Fore.RED+"Error: unable to run the model :flushed: \n"))
    
    except(FileNotFoundError):
        print(emojis.encode(colorama.Fore.RED+"Error: unable to run the model :unamused: \n"))


#for data processing, add something to choose which data processing script to run
@model.command()
@click.option('-d', default=False, help='Run the data processing script')
def data(**kwargs):
    print(emojis.encode(colorama.Fore.YELLOW+"Attempting to run data processing script:confused: \n"))
    colorama.Fore.RESET  


    try:
        subprocess.run(["python3" ,"Data_Processing/main.py"], check=True)    
        print(emojis.encode(colorama.Fore.GREEN+"The graphs should be in your browser! :smirk: \n"))
    
    except(KeyboardInterrupt):
        print(emojis.encode(colorama.Fore.RED+"You stopped the script running! :unamused: \n"))
    
    except subprocess.CalledProcessError as e:
        print(emojis.encode(colorama.Fore.RED+"Error: unable to display the graphs! :flushed: \n"))
    

@model.command()
@click.option('-p', default=False, help='Run the model with the specified properties file')
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
