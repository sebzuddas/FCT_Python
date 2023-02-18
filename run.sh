#!/bin/bash

## ----- Model Run Command ----- ##

# python3 FCT_Model/main.py FCT_Model/props/model.yaml

## ----- Different Approaches ----- ##
#APPROACH 1
#READS
# read -p "test:" testNumber
# echo "Test number: " $testNumber

#APPROACH 2
# # catch first arguments with $1
# case "$1" in
#  -s|--scan)
#   # execute if arguments in $1 to equal "-s" or "--scan"
#   echo "scan..."
#   ;;
#  *)
#   # else
#   echo "Usage: (-s|--scan)"
#   ;;
#  -r|--run)
#   echo "Run"
# esac

## ----- Styling Variables ----- ##
#Defining Colours
#Link for Colours
#https://misc.flogisoft.com/bash/tip_colors_and_formatting
RED='\033[0;31m' #make the text red
GREEN='\033[0;32m' #make the text green
NC='\033[0m' # No Colour

## ----- TODO List ----- ##
#TODO run with tests
#TODO run with different test parameters
#TODO help section to describe
  #TODO How to run the model
  #TODO what parameters mean what
  #TODO how to edit the parameters
  #TODO Look into error handling
#TODO 

## ----- Program ----- ##
while (( $# > 0 ))
do
    opt="$1"
    shift

    case $opt in
    -h|--help)
        helpfunc
        exit 0
        ;;
    -v|--version)
        echo "$0 version $version"
        exit 0
        ;;
    --file)  # Example with an operand
        filename="$1"
        shift
        ;;
    -r|--run)
      echo "Running Model..."
      
        python3 FCT_Model/main.py FCT_Model/props/model.yaml

      echo -e "${GREEN} Model run successfully! \n ${NC} Generating outputs..."
      
      
      Python3 Data_Processing/main.py



      ;;
    -*|--*)
        echo -e "${RED}Invalid option: ${NC}'$opt'" 
        echo -e "${NC}Please use ${GREEN}-h ${NC}for more information"
        exit 1
        ;;
    *)
        # end of long options
        break;
        ;;
   esac
done




