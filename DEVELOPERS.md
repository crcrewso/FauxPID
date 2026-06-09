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
- `DISPLAY_OPTIONS`

To add or remove options, update those lists and then wire the new option into `run_analysis(...)`.

## Notes

`dicom_analysis.py` expects generated `.dcm` files to exist under the output image tree and mirrors the folder structure when writing analysis text files.