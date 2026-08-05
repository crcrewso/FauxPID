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

## CAX Offset

These images show situations in which the center of the beam does not line up with the center of the image. This can be due to a variety reasons such as the beam not being around isocenter, the jaws being shifted or other issues.

## Field Size

Images here have differing field sizes. This can be caused by an edge of the jaw shifting (which should never happen) or more likely the edges of the MLC not being where you expect. 

## Flatness 

Images here have issues with field flatness. This was done by changing the height of the horns or creating a left/right gradient. This can be caused by beam steering issues or the flattening filter being defective or misaligned.  

## Symmetry

Images here have issues with symmetry in the left/right (x) direction or up/down (y) direction. This can be caused by beam steering issues, flattening filter misaligned or possibly issues with collimater angle. 

## Winston-Lutz

The generated images contain a bb near the center of the image with a simulated MLC "grid" pattern. Each set of images is seperated into subfolders. The images are from the perspective of the Beam's Eye View (BEV). 

Note that the gantry looking down from the ceiling corresponds to a gantry angle of $0^\circ$ in this dataset. 

The MLC is simulated using a combination of small negative bbs and lines combined with blurring. 