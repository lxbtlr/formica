# Scientific Computing Project 1: Formica
project by Alex Butler

## Install:

To install, clone this repository and install its dependencies.

```
git clone https://github.com/olincollege/scicomp-p1-formica.git
```

## Dependencies:
There are a few dependencies for this project that need to be installed for the code to function. 
- Python 3.10+
- Python Libraries:
    ```
    numpy
    pandas
    pygame
    ```
- (Optional) dependencies for other features:
    ```
    imagemagick
    ```

### Note 
Installing these libraies through your prefered method is fine -- I personally use nix :snowflake: to create a nix shell environment to load all dependencies easily from the default.nix file using the command:
```
nix-shell default.nix
```

# Usage

## side-note
One of my goals for this project was to practice refactoring the code base. This 
throughout the coding process, but most significantly in the last week on the refactor
branch. That code has been merged and does run **however**, you will immediately 
notice there is a problem... THE ANTS ARE ONLY IN ONE QUARTER OF THE SCREEN. The
earlier MVP is still accessible (look at src/_model.py) and you can see more accurate 
ants across your screen.


There are many arguments that can be passed into the script to modify the output 
of the code. However, to run the default/unchanged version you only need to run:
```
python model.py
```

To learn more about the arguments that can be passed into this model, run:
```
python model.py -h
```

# Simulation Settings & Configuration 


# High-level Code Overview
