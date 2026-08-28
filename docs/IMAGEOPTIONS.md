# Image Options

This document gives an overview of the different image types that can be generated: 

- [Artifacts](#artifacts)
- [CAX Offset](#cax-offset)
- [Field Size](#field-size)
- [Flatness](#flatness)
- [Symmetry](#symmetry)
- [Winston-Lutz](#winston-lutz)

## Artifacts 

Images here characterize issues with the detector device. Dead detectors, positive and negative ghosting are possible issues of the imaging device and not the beam itself. 

The `artifact_zero_4_columns_10x10` shows a set of dead detectors. The detectors are vertical and span 4 pixels horizontally (approximately 1.2-1.5 mm). This is an electrical issue moreso than just detectors. If a column readout line or multiplexer channel has an issue, it can cause a whole column to be "dead". 

The `artifact_detetctor_decrease_10x10` shows a decrease in dose small circular area. This negative ghosting could be caused by prior high dose fields. This can create a decrease in sensitivity in the amorphous silicon inside the EPID panel resulting in a negative ghosting effect.

Similarly, the `artifact_detetctor_increase_10x10` shows a increase in dose small circular area. This can be caused by defects in the panel where prior radiation exposure increases the sensitivity or baseline signal for subsequent readouts. Amorphous silicon has a high density of local structural defects causing shallow and deep electron traps. These electron traps may capture electrons in a prior dose causing negative ghosting but "priming" the scinitllator for the subsequent dose which has a local bright spot. 

The `artifact_vertical_bar_10x10` has a positive vertical bar. This corresponds to an issue with the EPID panel likely arising from circuitry issues. It can be a multiplexer or readout IC or other electrical issues in the panel.

## CAX Offset

These images show situations in which the center of the beam does not line up with the center of the image. This can be due to a variety reasons such as the beam not being around isocenter, the jaws being shifted or other issues.

Each field is shifted in the x direction, y direction or both. 

## Field Size

Images here have differing field sizes. This can be caused by an edge of the jaw shifting (which should never happen) or more likely the edges of the MLC not being where you expect. 

For example, `field_size_plus_5_mm_10x10` has an extra 5 mm on the right side giving a horizontal length of 10.5 cm. However, the metadata on the DCM file still says 10x10 cm. This is simulating a jaw out of position. 

Similarly, `field_size_rotated_5_degrees_10x10` has a 10x10 field rotated five degrees. The metadata does not reflect the rotation and expects a straight field. This is simulating a collimater out of position. 

## Flatness 

Images here have issues with field flatness. This was done by changing the height of the horns or creating a left/right gradient. This can be caused by beam steering issues or the flattening filter being defective or misaligned.  

`flatness_perfect_10x10` is an unrealistically perfect image. The field is perfectly flat and should simulate the "goal". 

`flatness_excess_horns_10x10` is an example of unrealistically large horns. It almost looks like an FFF image. 

The other images have very levels of flatness according to the different metrics. This is done by adjusting the size of the horns. These simulate varying degrees of effectiveness of the flattneing filter. Large errors are caused by the filter being misaligned, out of position or possibly malformed. 

## Symmetry

Images here have issues with symmetry in the left/right (x) direction or up/down (y) direction. This can be caused by beam steering issues, flattening filter misaligned or possibly issues with collimater angle. 

`symmetry_perfect_10x10` is an image that is perfectly symmetrical in both the x direction and y direction. 

`symmetry_positive_y_10x10` is an image with a gradient upwards. This shows a larger dose in the positive y direction which simulates a beam favoring the y direction or possibly a rotated flattening filter. 

Other images have varying degrees of a similar effect. `symmetry_x_and_y_gradient_10x10` shows both an x and y gradient. This is more realistic than having an error in only one direction. 

## Winston-Lutz

The generated images contain a bb near the center of the image with a simulated MLC "grid" pattern. Each set of images is seperated into subfolders. The images are from the perspective of the Beam's Eye View (BEV). 

Note that the gantry looking down from the ceiling corresponds to a gantry angle of $0^\circ$ in this dataset. 

The MLC is simulated using a combination of small negative bbs and lines combined with blurring. 


### Collimater Rotation

Collimater rotation does not change the observed position of the bb. Therefore, other than the MLC rotating, there should be no observed change in the image. 

### Couch Rotation

Couch rotation does change the position of the bb. If the bb was originally at some position $(x, y, z)$ where positive $x$ is to the right and positive $z$ is towards the ceiling, then a 45 degree couch rotation (counter-clockwise when viewing from above) moves the bb to 
$$\left(\frac{\sqrt 2}{2} x - \frac{\sqrt 2}{2} y, \frac{\sqrt 2}{2} x + \frac{\sqrt 2}{2} y, z\right)$$
This was found by rotating unit vectors in the $x$ direction and $y$ direction seperately and taking their sums. Note that this formula can be used twice to get a $90^\circ$ rotation, three times for a $135^\circ$ rotation, etc. 

### Gantry Rotation

The rotation of the gantry has the same effect as a couch rotation except along different axes. The $y$ axis is unaffected by the gantry rotation similar to the $z$ axis in the couch rotation. For a $45^\circ$ gantry rotation, we have
$$ \left(\frac{\sqrt 2}{2} x+ \frac{\sqrt 2}{2} z, y, -\frac{\sqrt 2}{2} x + \frac{\sqrt 2}{2} z\right) $$

Note that relatively speaking, a rotation of the gantry about the isocenter is the same as rotating the whole room (including the bb) about the isocenter while keeping the gantry still. This means we can pretend the bb rotates about the isocenter. 

To note, a rotation could cause the bb to appear larger or smaller based on the distance between the beam and the bb. 

### Handling projection with a non-zero z position

The beam coming out of a linear accelerator is not parallel. The beam comes from a single source position and thus, any z axis movement of the bb will cause the perceived position of the bb on the EPID to shift. Denote the z offset as $z$. If we assume the EPID panel is at isocenter, and we assume without loss of generality that the xy shift is just $x$, then we have

$$ \frac{SAD - z}{x} = \frac{SAD}{x_{projected}} $$

Where SAD is the Source-to-Axis Distance. This formula is because the position of the bb and the main axis of the beam along with the source creates a right triangle. This right triangle is similar to the right triangle created by the source and the projected x. Rearranging the formula we get

$$\frac{SAD}{SAD - z} \cdot x = x_{projected} $$

Which gives us a projection factor when we have any z offset. 

Note the standard SAD is 100 cm. Our maximum z offset used in these images is 7 mm with an SID of 100 cm (the detector is at isocenter). So at most we would have a projection factor of $\frac{100}{100 - 0.7} = 1.006$. This is too small for any actual difference since each pixel in an image is 0.336 mm. If the x offset and y offset was greater than 2 cm, this would matter. 

### Perfect

This set of images has the bb at the center. All images therefore see the bb at the same place. The only difference is the surrounding MLC. 

### 1mm right

Positionally the bb is at (1, 0, 0) where positive x is to the right and positive z is towards the ceiling when the gantry is at $0^\circ$. 

### 1mm out

Positionally the bb is at (0, -1, 0) where positive x is to the right and positive z is towards the ceiling when the gantry is at $0^\circ$. 

### Complex offset

Positionally the bb is at (2, 3, 6) which corresponds to a 7mm offset. 

### Wobble wobble

This case has the bb positionally at the same location as the complex offset of (2, 3, 6). However, the bb is moving in between images causing inconsistent positions. Each image is off by 1mm each time. 

### One off outlier

This case has the complex image set except a single image does not agree with the rest of the set of images. Specifically, "winston_lutz_outlier_gantry_315.dcm" is 5mm off in the x direction. 



