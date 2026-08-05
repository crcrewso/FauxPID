# Algorithms

The following classes of algorithms are used in this application:
- [Field Size](#field-size)
- [Flatness](#flatness)
- [Symmetry](#symmetry)

## Field size

This contains a single algorithm. 

### Field size

The field size is calculated by FWXM with a default to Full Width Half Max (FWHM). Provisionary boundaries are found using the max of the full profile. If the CAX is within those bounds, the 100% max is set to the CAX value and the boundaries are found using this new max. Otherwise, the bounds are found using the max of the whole profile. 

Note that where the transition falls between two indices (as is almost always the case), the indices closer to beam center are taken as the boundary. 

## Flatness

Contains four algorithms:
- [Flatness Calculation by Variance](#flatness-calculation-by-variance)
- [Flatness Calculation by Ratio (IEC)](#flatness-calculation-by-ratio-iec)
- [Flatness Calculation by CAX Variance](#flatness-calculation-by-cax-variance)
- [Flatness Calculation by CAX Ratio](#flatness-calculation-by-cax-ratio)

### Flatness Calculation by Variance

This is expressed as a percent value calculated over 80% of the field size. 
Uses the formula: 

$$ \text{metric} = \left( \frac{MAX-MIN}{MAX + MIN} \right) \cdot 100 $$
where $MAX$ is the maximum value in the region of interest (%80 of field size) and $MIN$ is the minimum value in the region of interest. 

This should be almost exactly the same to pylinac's Flatness (Difference) metric. The difference comes from off-by-one edge choices and possible other configuration choices. 

This formula comes from Sun Nuclear's IC Profiler Help under Flatness Calculation by Variance. 

### Flatness Calculation by Ratio (IEC)

This method of calculation is according to IEC Standard 976. It determines the flatness of the radiation profile, expressed as a percent value and calculated over a portion of the field size determined by the size of the field. If the field size is $X$, then

If 5 cm $< X \le$ 10 cm: X - 2 cm

If 10 cm $< X \le$ 30 cm: X * 0.8

Else $X \ge$ 30 cm: X - 6 cm

The Ratio (IEC) flatness calculation is
$$\text{metric} = \left( \frac{MAX}{MIN} \right) \cdot 100$$
where $MAX$ is the maximum over the above calculated region of interest. 

Note that pylinac's Flatness (Ratio) metric uses the same formula but considors 80% of the field as the region of interest. 

This formula comes from IEC 60976 flatness. 

### Flatness Calculation by CAX Variance

This method simply finds the maximum difference normalized to the CAX. 

$$ \text{metric} =\frac{\text{MAX}-\text{MIN}}{CAX}$$

where MAX is the maximum in a region, MIN is the minimum in a region, and CAX is the value at the central axis. The region used is the whole field. 

This formula comes from Sun Nuclear's IC Profiler Help under CAX Variance Flatness calculations. It may also be used with Varian's OEM analysis protocol. 

### Flatness Calculation by CAX Ratio

$$\text{metric} = \frac{MAX}{CAX}$$

where MAX is the maximum value within 90% of the field size and CAX is the value at CAX. 

This formula comes from Sun Nuclear's IC Profiler Help under CAX Ratio Flatness.

## Symmetry

Contains three algorithms:
- [Symmetry Calculation by CAX Point Difference](#symmetry-calculation-by-cax-point-difference)
- [Symmetry Calculation by Point Ratio (IEC 976)](#symmetry-calculation-by-point-ratio-iec-976)
- [Symmetry Calculation by Area](#symmetry-calculation-by-area)

### Symmetry Calculation by CAX Point Difference

This algorithm is found using the formula:

$$ \text{metric} = \frac{D_{sym} - D_{j}}{D_{CAX}} $$

where $D_{j}$ is the value at a position $j$ and $sym$ is the position symmetrical to $j$ with respect to the CAX. The position $j$ is chosen to create the largest difference. Note that some use this formula to find symmetry for an arbitrary or user chosen $j$. 

This formula comes from Sun Nuclear's IC Profiler Help under CAX Point Difference Symmetry. 

### Symmetry Calculation by Point Ratio (IEC 976)

This method of calculation is according to IEC Standard 976. It determines the symmetry of the radiation profile, expressed as a percent value and calculated over a portion of the field size determined by the size of the field. If the field size is $X$, then

If 5 cm $< X \le$ 10 cm: X - 2 cm

If 10 cm $< X \le$ 30 cm: X * 0.8

Else $X \ge$ 30 cm: X - 6 cm

Then the formula is:

$$ \text{metric} = \frac{D_{j}}{D_{sym}} \cdot 100\%$$

Where $D_j$ is the value at position $j$ and $sym$ is symmetrical to $j$ with respect to the cax. The position $j$ is chosen to create the largest difference (where $D_j > D_{sym}$). Note that some use this formula to find symmetry for an arbitrary or user chosen $j$. 

This formula comes from IEC 60976 and referenced by Sun Nuclear's IC Profiler Help under Point Ratio (IEC) Symmetry. 

### Symmetry Calculation by Area

This method compares the "area" under the profile between the two halves of the CAX. The formula is 

$$ \text{metric} = \frac{RS -LS}{RS + LS} \cdot 200\%$$

where RS is the right sum and LS is the left sum. Each sum is calculated using trapezoidal integration between each measured point on the left of the CAX and the right of the CAX to find the LS and RS respectively. 

This formula comes from Sun Nuclear's IC Profiler Help under Area Symmetry. 