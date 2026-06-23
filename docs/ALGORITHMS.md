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

This is expressed as a percent value calculated over %80 of the field size. 
Uses the formula: 

$$  \left( \frac{MAX-MIN}{MAX + MIN} \right) \cdot 100 $$
where $MAX$ is the maximum value in the region of interest (%80 of field size) and $MIN$ is the minimum value in the region of interest. 

This should be almost exactly the same to pylinac's Flatness (Difference) metric. The difference comes from off-by-one edge choices and possible other configuration choices. 

# Flatness Calculation by Ratio (IEC)

This method of calculation is according to IEC Standard 976. It determines the flatness of the radiation profile, expressed as a percent value and calculated over a portion of the field size determined by the size of the field. If the field size is $X$, then

If 5 cm $< X \le$ 10 cm: X - 2 cm

If 10 cm $< X \le$ 30 cm: X * 0.8

Else $X \ge$ 30 cm: X - 6 cm

The Ratio (IEC) flatness calculation is
$$ \left( \frac{MAX}{MIN} \right) \cdot 100$$
where $MAX$ is the maximum over the above calculated region of interest. 

Note that pylinac's Flatness (Ratio) metric uses the same formula but considors 80% of the field as the region of interest. 


## Symmetry

Contains three algorithms:
- Symmetry Calculation by CAX Point Difference
- Symmetry Calculation by Point Ratio (IEC 976)
- Symmetry Calculation by Area

# Symmetry Calculation by CAX Point Difference

This algorithm is found using 
