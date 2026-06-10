
from pathlib import Path
from datetime import datetime

from matplotlib import pyplot as plt
import numpy as np
import pydicom
from scipy import ndimage

from pylinac.core.image_generator import AS1200Image, AS1000Image
import pylinac.core.image_generator.layers as layers
from dicom_metadata import add_metadata


def generate_dicom_using_layers(file_out_name, layers):
    """
    Generates a DICOM file using the specified layers and saves it to the specified file_out_name. 
    Updates the metadata of the DICOM file using the add_metadata function. Also saves a PNG version of the image for reference.
    """
    as1200 = AS1200Image()
    for layer in layers:
        as1200.add_layer(layer)
    as1200.generate_dicom(file_out_name=file_out_name, gantry_angle=0)
    add_metadata(file_out_name, gantry_angle=0)
    plt.imsave(file_out_name.with_suffix('.png'), as1200.image)
    return as1200.image

def generate_artifacts_images(dir_path, dead_detector_field_position_percent : float = 0.3):
    """
    Generates DICOM files with artifacts at the specified directory path. 
    To make your own artifact images create a new AS1200Image, add a field layer, then modify as1200.image as needed. 
    The image is an array of pixel values that can be modified as needed to create the desired artifact. 
    """
    dir_path = dir_path / "Artifacts"
    dir_path.mkdir(parents=True, exist_ok=True)


    file_path = dir_path / "artifact_detector_decrease_10x10.dcm"
    as1200 = AS1200Image()
    as1200.add_layer(layers.FilteredFieldLayer(
        field_size_mm=(100, 100)
    ))
    subtractimage = AS1200Image()
    subtractimage.add_layer(layers.PerfectFieldLayer(
        field_size_mm=(5, 5),
        cax_offset_mm=(0, 10)
        #alpha=0.5
    ))
    as1200.image = as1200.image - 0.1 * subtractimage.image
    as1200.add_layer(layers.GaussianFilterLayer())
    as1200.generate_dicom(file_out_name=file_path, gantry_angle=0)
    add_metadata(file_path, gantry_angle=0)
    plt.imsave(file_path.with_suffix('.png'), as1200.image)


    file_path = dir_path / "artifact_detector_increase_10x10.dcm"
    as1200 = AS1200Image()
    as1200.add_layer(layers.FilteredFieldLayer(
        field_size_mm=(100, 100)
    ))
    addimage = AS1200Image()
    addimage.add_layer(layers.PerfectFieldLayer(
        field_size_mm=(5, 5),
        cax_offset_mm=(0, 10)
        #alpha=0.5
    ))
    as1200.image = as1200.image + 0.1 * addimage.image
    as1200.add_layer(layers.GaussianFilterLayer())
    as1200.generate_dicom(file_out_name=file_path, gantry_angle=0)
    add_metadata(file_path, gantry_angle=0)
    plt.imsave(file_path.with_suffix('.png'), as1200.image)


    file_path = dir_path / "artifact_vertical_bar_10x10.dcm"
    as1200 = AS1200Image()
    as1200.add_layer(layers.FilteredFieldLayer(
        field_size_mm=(100, 100)
    ))
    addimage = AS1200Image()
    addimage.add_layer(layers.PerfectFieldLayer(
        field_size_mm=(100, 5),
        cax_offset_mm=(0, 10)
        #alpha=0.5
    ))
    as1200.image = as1200.image + 0.5 * addimage.image
    as1200.add_layer(layers.GaussianFilterLayer())
    as1200.generate_dicom(file_out_name=file_path, gantry_angle=0)
    plt.imsave(file_path.with_suffix('.png'), as1200.image)


    file_path = dir_path / "artifact_zero_4_columns_10x10.dcm"
    as1200 = AS1200Image()
    as1200.add_layer(layers.FilteredFieldLayer(
        field_size_mm=(100, 100)
    ))
    as1200.add_layer(layers.GaussianFilterLayer())
    center_column = as1200.image.shape[1] // 2
    center_column_offset = int(as1200.image.shape[1] * dead_detector_field_position_percent)

    as1200.image[:, center_column - 40:center_column -36] = 0
    as1200.generate_dicom(file_out_name=file_path, gantry_angle=0)
    add_metadata(file_path, gantry_angle=0)
    plt.imsave(file_path.with_suffix('.png'), as1200.image)


def generate_flatness_images(dir_path):
    dir_path = dir_path / "Flatness"
    dir_path.mkdir(parents=True, exist_ok=True)

    perfect_open_field_layers = [
    layers.PerfectFieldLayer(
    field_size_mm=(100, 100), 
    alpha=1.0, 
    cax_offset_mm=(0, 0)), 
    layers.GaussianFilterLayer()
    ]
    file_path = dir_path / "flatness_perfect_10x10.dcm"
    as1200 = generate_dicom_using_layers(file_path, perfect_open_field_layers)
    

    field_layers = [
    layers.FilteredFieldLayer(
    field_size_mm=(100, 100), 
    alpha=1.0, 
    gaussian_height=0.1, 
    gaussian_sigma_mm=32.0,
    cax_offset_mm=(0, 0)), 
    layers.GaussianFilterLayer()
    ]
    file_path = dir_path / "flatness_excess_horns_10x10.dcm"
    as1200 = generate_dicom_using_layers(file_path, field_layers)

    field_layers = [
    layers.FilteredFieldLayer(
    field_size_mm=(100, 100), 
    alpha=1.0, 
    gaussian_height=0.03, 
    gaussian_sigma_mm=32.0,
    cax_offset_mm=(0, 0)), 
    layers.GaussianFilterLayer()
    ]
    file_path = dir_path / "flatness_filtered_10x10.dcm"
    as1200 = generate_dicom_using_layers(file_path, field_layers)

    field_layers = [
    layers.FilteredFieldLayer(
    field_size_mm=(100, 100), 
    alpha=1.0, 
    gaussian_height=0.03, 
    gaussian_sigma_mm=33.968,
    cax_offset_mm=(0, 0)), 
    layers.GaussianFilterLayer()
    ]
    file_path = dir_path / "flatness_two_percent_variance_10x10.dcm"
    as1200 = generate_dicom_using_layers(file_path, field_layers)

    field_layers = [
    layers.FilteredFieldLayer(
    field_size_mm=(100, 100), 
    alpha=1.0, 
    gaussian_height=0.03, 
    gaussian_sigma_mm=30.92,
    cax_offset_mm=(0, 0)), 
    layers.GaussianFilterLayer()
    ]
    file_path = dir_path / "flatness_two_percent_IEC_ratio_10x10.dcm"
    as1200 = generate_dicom_using_layers(file_path, field_layers)

    field_layers = [
    layers.FilteredFieldLayer(
    field_size_mm=(100, 100), 
    alpha=1.0, 
    gaussian_height=0.0222, 
    gaussian_sigma_mm=32,
    cax_offset_mm=(0, 0)), 
    layers.GaussianFilterLayer()
    ]
    file_path = dir_path / "flatness_two_percent_CAX_ratio_10x10.dcm"
    as1200 = generate_dicom_using_layers(file_path, field_layers)


    field_layers = [
        layers.FilterFreeFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]

    file_path = dir_path / "flatness_imperfect_fff_10x10.dcm"
    as1200 = generate_dicom_using_layers(file_path, field_layers)

