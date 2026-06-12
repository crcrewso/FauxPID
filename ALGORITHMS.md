### Algorithms

This file talks about specifics for each algorithm.

## Field size

This contains a single algorithm. 

# Field size

The field size is calculated by FWXM with a default to Full Width Half Max (FWHM). Provisionary boundaries are found using the max of the full profile. If the CAX is within those bounds, the 100% max is set to the CAX value and the boundaries are found using this new max. Otherwise, the bounds are found using the max of the whole profile. 

Note that where the transition falls between two indices (as is almost always the case), the indices closer to beam center are taken as the boundary. 

## Flatness

Contains four algorithms:
- Flatness Calculation by Variance
- Flatness Calculation by Ratio (IEC)
- Flatness Calculation by CAX Variance
- Flatness Calculation by CAX Ratio:

# Flatness Calculation by Variance

Uses the formula: 


## Symmetry

Contains three algorithms:
- Symmetry Calculation by CAX Point Difference
- Symmetry Calculation by Point Ratio (IEC 976)
- Symmetry Calculation by Area

# Symmetry Calculation by CAX Point Difference

This algorithm is found using 
