# Developer Notes

This project is organized around a small GUI entrypoint and a few helper modules that generate and analyze DICOM images.

## Entry Flow

`main.py` starts the GUI by creating `AnalysisGUI` from `analysis_gui.py` and calling `mainloop()`.

## GUI Behavior

`analysis_gui.py` is responsible for:

1. Letting the user choose an output directory.
2. Letting the user select image type options and display options.
3. Calling `run_analysis(...)` when the user clicks **Generate**.

## Generation and Analysis

`run_analysis(...)` currently:

1. Builds the output path under `DICOM_GENERATION_OUTPUT`.
2. Generates image files through `create_image.py`.
3. Runs analysis through `dicom_analysis.py`.

The generated files are written under:

- `DICOM_GENERATION_OUTPUT/IMAGES`
- `DICOM_GENERATION_OUTPUT/ANALYSIS`

## Customizing Options

The checkbox labels shown in the GUI come from these lists in `analysis_gui.py`:

- `IMAGE_TYPE_OPTIONS`
- `OTHER_OPTIONS`

To add or remove options, update those lists and then wire the new option into `run_analysis(...)`.

## Customizing Analysis

To add/edit algorithms, all metrics live in `metrics.py`. Using the same framework, create a new class for your algorithm and implement a `calculate()` function. 

## Customizing Images

All images are generated using pylinac's Image Generator. This all lives in `create_image.py`. You can use the `generate_dicom_using_layers()` function and specify the layers or for more complex images, you can do it yourself (see the artifacts images). 

## Saving as a single file executable

The `FauxPID.spec` contains the specifications for how to convert the file. Developers just need to run
`pyinstaller --clean FauxPID.spec` to use the spec. 

## Notes

### Open question: profile centering

`run_analysis_on_path` in `metrics.py` analyzes with `Centering.BEAM_CENTER`. This needs exploration before the CAX-based results can be trusted for offset fields:

- `Centering.NONE` may be the more appropriate choice, so that profiles are taken through the image centre (the CAX for these simulated images) rather than through the detected beam centre.
- The metrics locate the CAX in two different ways: pylinac's `profile.cax_index`, and `get_cax_value()`, which averages the middle element(s) of the profile array. If the centering mode makes these disagree, metrics such as CAX Offset from Beam Center, CAX Variance/Ratio flatness and CAX Point Difference symmetry may use a CAX value from a different pixel than the CAX index.

Suggested exploration: generate the CAX Offset images, run the analysis with each centering mode, and compare `profile.cax_index` with the array midpoint and the known offset.
