# Team-Virus-2020

This code runs agent-based modeling simulations using the Mesa package in Python.

To run simulations on your computer, create a new virtual environment and
install Mesa following these instructions: https://mesa.readthedocs.io/en/master/

The code is written to view and run simulations using a web-based GUI.
There are 3 files:
model.py defines the model, agents, and each step that advances the model
server.py contains code to visualize the model and any associated graphs
run.py contains code needed to run the model

To run from the terminal, navigate to the directory containing these 3 files and type:
$ mesa runserver

To run in batch mode, adjust desired parameters in br_params list and type:
$ python model.py
This will create a single csv file with the output data for each run 
