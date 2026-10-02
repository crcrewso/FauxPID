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
2. Generates image files through `ImageGenerator` in `images/create_image.py`.
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

All images are generated using pylinac's Image Generator. The code lives in `FauxPID/images/`:

- `create_image.py` — `ImageGenerator`, the class the GUI uses. Each `generate_*_images()` method writes one folder of images by calling a function in one of the modules below.
- `base.py` — `BaseImageGenerator`: creating simulators (`new_simulator()`), output folders (`output_dir()`) and saving DICOM/PNG files with metadata (`save()`, `generate_dicom_using_layers()`).
- `profiles.py` — CAX offset, field size, flatness, symmetry and penumbra images. Most images are a row in a table near the generator function (e.g. `FLATNESS_HORNS`, `SYMMETRY_SLOPES`), so adding a variant is usually one line.
- `artifacts.py` — images that edit the pixel array directly instead of only stacking layers.
- `winston_lutz.py` — Winston-Lutz images. Each folder is a `WinstonLutzScenario` in `SCENARIOS`, listing the projected BB offset for each collimator, couch and gantry angle.

For simple images, use `generate_dicom_using_layers()` with a list of layers. For more complex images, build a simulator with `new_simulator()`, modify `simulator_instance.image` as needed and call `save()` (see `artifacts.py`). 

## Saving as a single file executable

The `FauxPID.spec` contains the specifications for how to convert the file. Developers just need to run
`pyinstaller --clean FauxPID.spec` to use the spec. 

## Notes

### Open question: profile centering

`run_analysis_on_path` in `metrics.py` analyzes with `Centering.BEAM_CENTER`. This needs exploration before the CAX-based results can be trusted for offset fields:

- `Centering.NONE` may be the more appropriate choice, so that profiles are taken through the image centre (the CAX for these simulated images) rather than through the detected beam centre.
- The metrics locate the CAX in two different ways: pylinac's `profile.cax_index`, and `get_cax_value()`, which averages the middle element(s) of the profile array. If the centering mode makes these disagree, metrics such as CAX Offset from Beam Center, CAX Variance/Ratio flatness and CAX Point Difference symmetry may use a CAX value from a different pixel than the CAX index.

Suggested exploration: generate the CAX Offset images, run the analysis with each centering mode, and compare `profile.cax_index` with the array midpoint and the known offset.
