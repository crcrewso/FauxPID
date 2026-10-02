# FauxPID

FauxPID generates synthetic ("faux") EPID DICOM images with known, built-in defects, such as an offset CAX, a tilted profile or a misplaced Winston-Lutz BB. It can also analyze them with a set of flatness, symmetry and field size metrics. Because the right answer is known for every image, you can use them to check QA software (or this project's own metrics) against a reference.

## Setup

You need Python 3.12 and [uv](https://docs.astral.sh/uv/). From the project folder:

```bash
uv sync
```

This creates a `.venv` virtual environment and installs all dependencies.

If you'd rather use pip, `requirements.txt` is generated from `uv.lock` and can be installed with `pip install -r requirements.txt`.

## How to use

1. Start the app:
   ```bash
   uv run python -m FauxPID.app.main
   ```
2. Choose an output directory.
3. Select the image types you want (see [docs/IMAGEOPTIONS.md](docs/IMAGEOPTIONS.md)).
4. Select any other options:
   - **Run analysis on generated images**: analyze every generated DICOM (off by default).
   - **Include PNG with each DICOM**: save a PNG preview next to each image.
   - **Results as JSON**: write analysis results as `.json` instead of `.txt`.
   - **Open output folder after generation**
5. Click **Generate**.

Your selections are remembered in `~/.FauxPID/settings.toml`.

## What gets created

The output directory will contain a `DICOM_GENERATION_OUTPUT` folder:

```
DICOM_GENERATION_OUTPUT/
  Images/       # one subfolder per image type, e.g. Images/Flatness/flatness_perfect_10x10.dcm
  Analysis/     # one result file per image, mirroring Images/ (only if analysis is enabled)
  Resources/
```

For the format of the analysis results, see [docs/RESULTS.md](docs/RESULTS.md).

## Resources

Files placed in a `resources/` folder at the project root are copied into the output when images are generated. A subfolder named after an image type (e.g. `resources/Winston-Lutz/`) is copied into that image type's folder. See [docs/RESOURCES.md](docs/RESOURCES.md).

## Analysis algorithms

For the formula and source of each metric, read [docs/ALGORITHMS.md](docs/ALGORITHMS.md).

## Running the tests

```bash
uv run pytest
```

Many tests are placeholders that are skipped as "not yet implemented". Their descriptions list what still needs testing.

## For developers

- [docs/DEVELOPERS.md](docs/DEVELOPERS.md) explains how the app works internally, how to add images and metrics, and how to build a single-file executable with PyInstaller.
- [AGENTS.md](AGENTS.md) gives guidance for contributors using AI coding tools.
