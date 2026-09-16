# Assignment 2 - Metabolic Modelling

This notebook investigates what happens in the E.coli core model with estimated maximal activity through metabolic modelling with COBRApy.

The model uses two files
- e_coli_core.json
    - The E.coli core model to be loaded in using COBRApy
- KEN3170_Assignment_2026_e_coli_core_expression.csv
    - The estimated maximal activity of biomass production.

## What this notebook does

With the use of the online model
- https://escher.github.io/#/app?map=e_coli_core.Core%20metabolism&tool=Builder&scrollToZoom=true&model=e_coli_core 
- It investigates the nature of the model:
    - Varying flux rates between reactions
    - Distinction between zero flux and no data.

It sets the estimated maximal flux rates from the CSV to the model with some extra constraints and carries out a Flux Balance Analysis (FBA) optimization of biomass production under varying glucose exchange rates.


## Requirements

- jupyter notebook

#### libraries
- cobra
- pandas
- matplotlib.pyplot
- numpy

## How to run

Use a python environment or venv with the installed libraries as your interpreter in the jupyter notebook.
To install the libraries:
- pip install cobra pandas matplotlib numpy

