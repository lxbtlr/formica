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
#### Nix
Installing these libraies through your prefered method is fine -- I personally use nix :snowflake: to create a nix shell environment to load all dependencies easily from the default.nix file using the command:
```
nix-shell default.nix
```
#### Additional Dependencies
If you look across the files in this repository, you may notice there are a few extra libraries 
then mentioned in the dependencies section. While they are being used, they're very pheripheral 
and do not impact how the code functions to simulating ants, instead, they mostly helped with debugging
or working with the code a little bit nicer (the biggest offenders are ArgParse & csv)

# Usage

There are many arguments that can be passed into the script to modify the output 
of the code. However, to run the default/unchanged version you only need to run:
```
python model.py
```

To learn more about the arguments that can be passed into this model, run:
```
python model.py -h
```

### side-note
One of my goals for this project was to practice refactoring the code base. This 
throughout the coding process, but most significantly in the last week on the refactor
branch. That code has been merged and does run **however**, you will immediately 
notice there is a problem... THE ANTS ARE ONLY IN ONE QUARTER OF THE SCREEN. The
earlier MVP is still accessible (look at src/_model.py) and you can see more accurate 
ants across your screen.

# Interesting Tidbits

One of the major outcomes from the refactor was the change in program architecture from
one main file to multiple files with distinct roles. Since the main goal of the refactor 
was to "make the code better", one angle I investigated was runtime. I got the 
idea that a major time sink might have been the display but I needed to prove it. 
To that end I created the timing decorator function (see src/helperfunctions.py) to record how long it takes for a given function to
execute each time it is called. To make that data more useful I added a few functions 
to compute useful metrics and boom, you get the [[Example table]] below. This became important 
as it revealed to me that the refactored version of my display function was 
actually much slower than my original... so much so that I reverted back to the 
original draw function. 

## Example table
| function | Mean | Median | Standard Deviation | Variance | Min | Max | Count | Total Time |
| -------- | ---- | ------ | ------------------ | -------- | --- | --- | ---------- | ---------- |
| tk init | 1.139548e-05 | 1.096725e-05 | 2.345531e-06 | 5.501515e-12 | 1.430511e-06 | 2.0504e-05 | 103 | 0.001173735 |
| sim mk folder path | 8.511543e-05 | 8.511543e-05 | 0.0 | 0.0 | 8.511543e-05 | 8.511543e-05 | 1 | 8.511543e-05 |
| sim init | 0.1143568 | 0.1143568 | 0.0 | 0.0 | 0.1143568 | 0.1143568 | 1 | 0.1143568 |
| agent init | 5.645037e-05 | 5.435944e-05 | 8.933405e-06 | 7.980572e-11 | 4.577637e-05 | 0.0001056194 | 100 | 0.005645037 |
| agent pos | 3.573892e-07 | 2.384186e-07 | 3.018333e-07 | 9.110332e-14 | 0.0 | 4.076958e-05 | 95419 | 0.03410172 |
| agent getadj | 1.486691e-06 | 1.430511e-06 | 7.843097e-07 | 6.151418e-13 | 4.768372e-07 | 3.361702e-05 | 95050 | 0.14131 |
| agent update t | 5.21092e-07 | 4.768372e-07 | 3.210982e-07 | 1.031041e-13 | 0.0 | 2.932549e-05 | 95050 | 0.04952979 |
| hf sat2fid | 1.33229e-06 | 1.192093e-06 | 5.983104e-07 | 3.579754e-13 | 4.768372e-07 | 4.172325e-05 | 95050 | 0.1266341 |
| hf flip | 1.939447e-06 | 1.66893e-06 | 1.166129e-06 | 1.359857e-12 | 7.152557e-07 | 6.484985e-05 | 119311 | 0.2313974 |
| tk calc | 1.875398e-05 | 1.978874e-05 | 8.174698e-06 | 6.682568e-11 | 2.861023e-06 | 0.0003857613 | 132045 | 2.47637 |
| hf d2pos | 5.748971e-05 | 5.912781e-05 | 1.44847e-05 | 2.098067e-10 | 3.361702e-05 | 0.0006928444 | 104902 | 6.030786 |
| agent forking | 0.0001501896 | 7.843971e-05 | 0.0001274237 | 1.62368e-08 | 4.267693e-05 | 0.001280546 | 90339 | 13.56798 |
| hf roll8 | 7.310338e-05 | 7.414818e-05 | 1.884655e-05 | 3.551924e-10 | 3.409386e-05 | 0.0002217293 | 14563 | 1.064605 |
| agent explore | 0.0002533828 | 0.0002632141 | 5.904198e-05 | 3.485955e-09 | 0.0001366138 | 0.0008790493 | 14563 | 3.690014 |
| agent update | 0.000465262 | 0.0003960133 | 0.0002067319 | 4.273807e-08 | 0.0001940727 | 0.002693892 | 95050 | 44.22315 |
| agent lost | 4.005407e-07 | 4.768372e-07 | 2.314091e-07 | 5.355017e-14 | 0.0 | 2.884865e-05 | 95050 | 0.03807139 |
| sim update p | 0.000158982 | 0.0001637936 | 3.970805e-05 | 1.576729e-09 | 6.985664e-05 | 0.0003700256 | 1000 | 0.158982 |
| sim update | 0.02478745 | 0.02749264 | 0.004979242 | 2.479285e-05 | 0.01625395 | 0.03272843 | 1000 | 24.78745 |
| sim metrics | 0.0001729181 | 0.0001847744 | 3.200513e-05 | 1.024328e-09 | 0.0001168251 | 0.0003437996 | 1000 | 0.1729181 |
| sim write | 0.0004688888 | 0.0004802942 | 7.263637e-05 | 5.276042e-09 | 0.000341177 | 0.001063347 | 1000 | 0.4688888 |
| hf rot45 | 6.453064e-06 | 6.437302e-06 | 2.124696e-06 | 4.514333e-12 | 3.099442e-06 | 0.0002686977 | 91433 | 0.590023 |
| sim save | 0.003205899 | 0.003151178 | 0.001552319 | 2.409694e-06 | 0.00201273 | 0.01074982 | 101 | 0.3237958 |
| agent reset | 1.516058e-05 | 1.525879e-05 | 3.70704e-06 | 1.374215e-11 | 6.914139e-06 | 3.695488e-05 | 369 | 0.005594254 |
| hf boardnorm | 0.03534937 | 0.03534937 | 0.0 | 0.0 | 0.03534937 | 0.03534937 | 1 | 0.03534937 |
| hf savefig | 0.2217147 | 0.2217147 | 0.0 | 0.0 | 0.2217147 | 0.2217147 | 1 | 0.2217147 |

