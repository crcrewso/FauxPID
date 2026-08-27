# DICOM Image Suite

This project provides a simple GUI for generating DICOM images and running analysis on the output.

## Setup 

You may need to install Python (3.12) first. 
Using UV:

1. Create a new virtual environment using `uv venv .venv`
2. Activate it if you haven't already: `.venv/Scripts/Activate.ps1`
3. Download dependencies using `uv sync`

## How to Use

1. Run `python -m FauxPID.app.main`.
2. Choose an output directory.
3. Select the image options you want.
4. Click **Generate**.

The app will create the DICOM images and run the analysis automatically.

## What Gets Created

The selected output directory will contain a `DICOM_GENERATION_OUTPUT` folder with generated images and analysis results.

## Analysis algorithms

For more on the specifics of each algorithm, read [ALGORITHMS.md](ALGORITHMS.md)

## For Developers

If you want to understand how the app works internally, read [DEVELOPERS.md](DEVELOPERS.md).
