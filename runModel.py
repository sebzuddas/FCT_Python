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
import traceback





####################  Functions  ####################

def update_parameter(parameter_name, new_value, yaml_file):
    with open('FCT_Model/props/model/model.yaml', 'r') as file:
        params = yaml.safe_load(file)

    params[parameter_name] = new_value

    with open(yaml_file, 'w') as file:
        yaml.safe_dump(params, file)

    
@click.group()
def model():
    pass

@model.command()
@click.option('--param', default=None, help='Parameter to change, default is number of iterations (weeks)')
@click.option('--value', default=None, help='New value for the parameter, if no given parameter this is the number of iterations')
@click.option('--years', default=None, help='Number of years to run the model for')
def run(param, value, years):
    print(emojis.encode(colorama.Fore.BLUE+"Attempting to run the model :confused: \n"))
    colorama.Fore.RESET  

    if years is not None:
        iterations = int(years)*52
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        dynamic_props = props_file_location+"/model-"+str(iterations)+'-'+dt_string+".yaml"
        update_parameter('stop.at', int(iterations), dynamic_props)
        yaml_location = dynamic_props


    elif param is not None and value is not None:
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
        yaml_location = props_file_location+'/standard.yaml'


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
@click.option('--sim', default=None, help='Simulation Number to run the data processing script on')
@click.option('--vis', is_flag=True, help='Visualise the data from the data processing script: True or False')
def data(sim, vis):
    print(emojis.encode(colorama.Fore.YELLOW+"Attempting to run data processing script:confused: \n"))
    colorama.Fore.RESET

    vis = str(vis)

    try:
        if sim != None and vis != None:
            
            print(f"Visualising simulation number: {sim}, placing into simulation_data as PC_{sim}\n")
            try:
                subprocess.run(["python3" ,"Data_Processing/main.py", props_file_location+'/model.yaml', sim, vis], check=True)  
                print(emojis.encode(colorama.Fore.GREEN+"The graphs should be in your browser! :smirk: \n"))
            except subprocess.CalledProcessError as e:
                print(emojis.encode(colorama.Fore.RED+f"Error: unable to run the data processing script: {e}\n"))
            except Exception:
                print(emojis.encode(colorama.Fore.RED+"Unknown error occurred:"))
                traceback.print_exc(file=sys.stdout)

        elif sim != None:
            print(f"placing simulation:{sim} into simulation_data as PC_{sim}\n")
            try:
                subprocess.run(["python3" ,"Data_Processing/main.py", props_file_location+'/model.yaml', sim, False], check=True)
                print(emojis.encode(colorama.Fore.GREEN+"The simulation data should be in the simulation_data folder! :smirk: \n"))
            except:
                print(emojis.encode(colorama.Fore.RED+"Error: unable to run the data processing script :flushed: \n"))

        else:
            subprocess.run(["python3" ,"Data_Processing/main.py", props_file_location+'/model.yaml', sim], check=True)

        
    except(KeyboardInterrupt):
        print(emojis.encode(colorama.Fore.RED+"You stopped the script running! :unamused: \n"))
    
    except subprocess.CalledProcessError as e:
        print(emojis.encode(colorama.Fore.RED+"Error: unable to display the graphs! :flushed: \n"))




@model.command()
@click.option('--all', is_flag=True, help='Run the model with all the different parameter settings outlined by the .YAML files')
@click.option('--lhs', default=None, help='Generate a Latin Hypercube Sample of the parameter space')
@click.option('--delete', is_flag=True, help='Delete all the .yaml files in the test_parameters folder')
def experiments(all, lhs, delete):

    
    test_folder_path = project_folder+'FCT_Model/props/model/test_parameters'
    number_existing_yaml_files = len([f for f in os.listdir(test_folder_path) if os.path.isfile(os.path.join(test_folder_path, f))])
    ### check for input ###
    #get_existing_number of yaml files. 
    print(f'Currently, there exist {number_existing_yaml_files} yaml files in the experiment folder.\n')
    if not all and not lhs and not delete:
        print("please specify either --all, --lhs, or --delete\n")  

    if number_existing_yaml_files == 0 and lhs == None:
        print('There are no yaml files in the experiment folder.\nPlease generate some yaml files using the --lhs flag, followed by the number of desired yaml files.\n')
        exit()
        
    if delete == True:
        prompt = input('Are you sure you want to delete all the yaml files in the test_parameters folder? (y/n): ')
        if prompt == 'y':
            print('Deleting all the yaml files in the test_parameters folder!\n')
            for f in os.listdir(test_folder_path):
                os.remove(os.path.join(test_folder_path, f))
            print('All the yaml files have been deleted!\n')
        else:
            print('No yaml files have been deleted!\nexiting...')
            exit()

    if all == False and lhs != None:
        #Generate the number of yaml files specified by lhs
        if number_existing_yaml_files > 0:
            delete_all_files = input(f'There are already {number_existing_yaml_files} files in the test_parameters folder, would you like to delete them? (y/n): ')
            if delete_all_files == 'y':
                for f in os.listdir(test_folder_path):
                    os.remove(os.path.join(test_folder_path, f))
                print('All the yaml files have been deleted!\n')

        print(emojis.encode(colorama.Fore.BLUE+f"Generating: {lhs} .yaml files 🥳 "))
        try:
            subprocess.run(["python3" ,"Experiment_Generator/main.py", lhs], check=True)
            print(emojis.encode(colorama.Fore.GREEN+"The yaml files should be in the props folder! :smirk: \n"))
        except subprocess.CalledProcessError as e:
            print(emojis.encode(colorama.Fore.RED+f"Error: unable to generate the yaml files: {e}\n"))
        except Exception:
            print(emojis.encode(colorama.Fore.RED+"Unknown error occurred:"))
            traceback.print_exc(file=sys.stdout)

    elif all == True and lhs == None:   
        #check that there are enough yaml files
        #run through the number of yaml files that exist
        if number_existing_yaml_files == 0:
            print('There are no yaml files in the test_parameters folder!\nexiting...')
            exit()

        print(colorama.Fore.RED+"WARNING: The following code will delete all previous simulation csv data in Data_Procsiing/outputs, as well as in FCT_Model/outputs")
        run_all = input(colorama.Fore.CYAN+f'Are you sure you want to run the model with {number_existing_yaml_files} the yaml files in the test_parameters folder? (y/n): ')

        if run_all == 'y':
            
            model_outputs = 'FCT_Model/outputs/'
            data_processing_outputs = project_folder+'Data_Processing/outputs/'
            print('Deleting all the csv files in the FCT_Model/outputs folder!\n')

            for file_name in os.listdir(model_outputs):
                if re.match(r'(agent|theory)_logger_out(_\d+)?\.csv$', file_name) and file_name != 'agent_logger_out.csv' and file_name != 'theory_logger_out.csv':
                    file_path = os.path.join(model_outputs, file_name)
                    os.remove(file_path)

            for file_name in os.listdir(model_outputs):
                print(file_name)

            # for file_name in os.listdir(data_processing_outputs):
            #     print(file_name)

            print('Deleting all the csv files in the Data_Processing/outputs folder!\n')
            for file_name in os.listdir(data_processing_outputs):
                if file_name.endswith('.csv'):
                    file_path = os.path.join(data_processing_outputs, file_name)
                    os.remove(file_path)

            print('All the csv files have been deleted!\n')

            database_override = input(colorama.Fore.RED+'Do you want to automatically ovewrite data in the database? (y/n): ')

            print(emojis.encode(colorama.Fore.BLUE+f"Running the model with {colorama.Fore.YELLOW}{number_existing_yaml_files}{colorama.Fore.BLUE} yaml files! 🥳 "))
            with alive_bar(number_existing_yaml_files, title=colorama.Fore.GREEN+"Running LHS Experiments"+colorama.Fore.RESET, bar='classic') as bar:
                for i, _ in enumerate(range(1, number_existing_yaml_files + 1), 1):
                    print(emojis.encode(colorama.Fore.BLUE+f"\nRunning the model with yaml file {colorama.Fore.YELLOW}{i}{colorama.Fore.BLUE}! 🥳 \n"))
                    run_model(i)
                    put_csv_to_database(i, database_override)
                    bar()

            print(emojis.encode(colorama.Fore.GREEN+"The experiments should be completed, well done! :smirk: \n"))
        else:
            print('No yaml files have been run!\nexiting...')
            exit()


    

    if all == True and lhs != None:
        pass
        #generate the yaml files
        
        #run the model with the yaml files


def put_csv_to_database(experiment_number, user_input):

    user_input = str(user_input)

    try:
        subprocess.run(["python3" ,"Data_Processing/main.py", props_file_location+'/model.yaml', str(experiment_number)],input=user_input, text=True, check=True)  
        # ctx = click.Context(data)
        # ctx.params = {'sim': experiment_number}
        # dataobj = data.make_context('data', [])
        # data.invoke(dataobj)
    except Exception as e:
        print(f"Unknown error occurred: {e}")

def run_model(experiment_number):
    try:
        with open('/dev/null', 'w') as devnull:
            subprocess.run(["python3", "FCT_Model/main.py", props_file_location+f"/test_parameters/test_{experiment_number}.yaml"], check=True, stdout=devnull, stderr=devnull)
        # subprocess.run(["python3" ,"FCT_Model/main.py", props_file_location+f"/test_parameters/test_{experiment_number}.yaml"], check=True)
    except subprocess.CalledProcessError as e:
        print(emojis.encode(colorama.Fore.RED+f"Error: unable to run the model: {e}\n"))
    except Exception:
        print(emojis.encode(colorama.Fore.RED+"Unknown error occurred:"))
        traceback.print_exc(file=sys.stdout)
        

if __name__ == "__main__":
    project_folder = os.environ.get('FCT_PROJECT_FOLDER')
    props_file_location = 'FCT_Model/props/model'
    colorama.init()
    model()