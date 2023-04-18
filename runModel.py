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
from colorama import Fore, Back, Style
import emojis
import subprocess
import yaml
from datetime import datetime
import re
import subprocess
from alive_progress import alive_bar
from repast4py import parameters





####################  Functions  ####################

def update_parameter(parameter_name, new_value, yaml_file):
    with open('FCT_Model/props/model/model.yaml', 'r') as file:
        params = yaml.safe_load(file)

    params[parameter_name] = new_value

    with open(yaml_file, 'w') as file:
        yaml.safe_dump(params, file)


# def main():
#     #  while True:
#     #     print(colorama.Fore.BLACK, colorama.Back.WHITE)
#     #     print(emojis.encode("Welcome to the Fundamental Cause Theory Agent Based Model!🥳 \n"))
#     #     # print(colorama.Style.RESET_ALL)
#     #     command = input("Enter command (type 'exit' to quit): ")
#     #     if command.lower() == 'exit':
#     #         break
    
@click.group()
def model():
    pass

@model.command()
@click.option('--param', default=None, help='Parameter to change, default is number of iterations (weeks)')
@click.option('--value', default=None, help='New value for the parameter, if no given parameter this is the number of iterations')
def run(param, value):
    print(emojis.encode(colorama.Fore.BLUE+"Attempting to run the model :confused: \n"))
    colorama.Fore.RESET  

    if param is not None and value is not None:
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        dynamic_props = props_file_location+"/model-"+str(param)+'-'+str(value)+'-'+dt_string+".yaml"
        update_parameter(param, int(value), dynamic_props)
        yaml_location = dynamic_props

    elif value is not None:
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        dynamic_props = props_file_location+"/model-"+str(value)+'-'+dt_string+".yaml"
        update_parameter('stop.at', int(value), dynamic_props)
        yaml_location = dynamic_props

    else:
        yaml_location = props_file_location+'/model.yaml'


    try:
        # print(yaml_location)
        # if value == None:
        #     value = 10

        # with alive_bar(int(value), title="Running the model", bar="notes") as bar:
        #     # Start running the model in a subprocess and capture the output
        #     process = subprocess.Popen(["python3", "FCT_Model/main.py", yaml_location], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        #     # Parse the output for tick information and update the progress bar
        #     for line in process.stdout:
        #         print(line, end="")  # Print the line to the terminal
        #         match = re.search(r'Tick: (\d+)', line)
        #         if match:
        #             tick = int(match.group(1))
        #             bar(tick)  # Update the progress bar

        #     # Wait for the subprocess to finish and check the return code
        #     process.wait()
        
        #     if process.returncode == 0:
        #         print(emojis.encode(colorama.Fore.GREEN + "Model run successfully! :smirk: \n"))
        #     else:
        #         print(emojis.encode(colorama.Fore.RED + "Model run failed! :disappointed: \n"))

        subprocess.run(["python3" ,"FCT_Model/main.py", yaml_location], check=True)
        print(emojis.encode(colorama.Fore.GREEN+"Model run successfully! :smirk: \n"))
        
    except(KeyboardInterrupt):
        print(emojis.encode(colorama.Fore.RED+"You stopped the model running! :unamused: \n "))
    
    except subprocess.CalledProcessError as e:
        print(emojis.encode(colorama.Fore.RED+"Error: unable to run the model :flushed: \n"))
    
    except(FileNotFoundError):
        print(emojis.encode(colorama.Fore.RED+"Error: unable to run the model - file not found :unamused: \n"))


#for data processing, add something to choose which data processing script to run
@model.command()
@click.option('-d', default=False, help='Run the data processing script')
def data(**kwargs):
    print(emojis.encode(colorama.Fore.YELLOW+"Attempting to run data processing script:confused: \n"))
    colorama.Fore.RESET  

    try:
        subprocess.run(["python3" ,"Data_Processing/main.py", props_file_location+'/model.yaml'], check=True)    
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

if __name__ == "__main__":
    props_file_location = 'FCT_Model/props/model'
    colorama.init()
    model()