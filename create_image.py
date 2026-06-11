
from pathlib import Path
from datetime import datetime

from matplotlib import pyplot as plt
import numpy as np
import pydicom
from scipy import ndimage

from pylinac.core.image_generator import AS1200Image
from pylinac.core.image_generator.simulators import Simulator
import pylinac.core.image_generator.layers as layers
from dicom_metadata import add_metadata

class ImageGenerator:
    def __init__(self, file_out_directory : Path, simulator: type[Simulator] = AS1200Image, sid=1000):
        self.file_out_directory = file_out_directory
        self.sid = sid
        self.simulator = simulator

    def generate_dicom_using_layers(self, file_out_name, layers):
        """
        Generates a DICOM file using the specified layers and saves it to the specified file_out_name. 
        Updates the metadata of the DICOM file using the add_metadata function. Also saves a PNG version of the image for reference.
        """
        simulator_instance = self.simulator(sid=self.sid)
        for layer in layers:
            simulator_instance.add_layer(layer)
        simulator_instance.generate_dicom(file_out_name=file_out_name, gantry_angle=0)
        add_metadata(file_out_name, gantry_angle=0)
        plt.imsave(file_out_name.with_suffix('.png'), simulator_instance.image)
        return simulator_instance

    def generate_artifacts_images(self, dead_detector_field_position_percent : float = 0.3):
        """
        Generates DICOM files with artifacts at the specified directory path. 
        To make your own artifact images create a new simulator_instance, add a field layer, then modify simulator_instance.image as needed. 
        The image is an array of pixel values that can be modified as needed to create the desired artifact. 
        """
        dir_path = self.file_out_directory / "Artifacts"
        dir_path.mkdir(parents=True, exist_ok=True)


        file_path = dir_path / "artifact_detector_decrease_10x10.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
            field_size_mm=(100, 100)
        ))
        subtractimage = self.simulator(sid=self.sid)
        subtractimage.add_layer(layers.PerfectFieldLayer(
            field_size_mm=(5, 5),
            cax_offset_mm=(0, 10)
            #alpha=0.5
        ))
        simulator_instance.image = simulator_instance.image - 0.1 * subtractimage.image
        simulator_instance.add_layer(layers.GaussianFilterLayer())
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0)
        plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)


        file_path = dir_path / "artifact_detector_increase_10x10.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
            field_size_mm=(100, 100)
        ))
        addimage = self.simulator(sid=self.sid)
        addimage.add_layer(layers.PerfectFieldLayer(
            field_size_mm=(5, 5),
            cax_offset_mm=(0, 10)
            #alpha=0.5
        ))
        simulator_instance.image = simulator_instance.image + 0.1 * addimage.image
        simulator_instance.add_layer(layers.GaussianFilterLayer())
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0)
        plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)


        file_path = dir_path / "artifact_vertical_bar_10x10.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
            field_size_mm=(100, 100)
        ))
        addimage = self.simulator(sid=self.sid)
        addimage.add_layer(layers.PerfectFieldLayer(
            field_size_mm=(100, 5),
            cax_offset_mm=(0, 10)
            #alpha=0.5
        ))
        simulator_instance.image = simulator_instance.image + 0.5 * addimage.image
        simulator_instance.add_layer(layers.GaussianFilterLayer())
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)


        file_path = dir_path / "artifact_zero_4_columns_10x10.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
            field_size_mm=(100, 100)
        ))
        simulator_instance.add_layer(layers.GaussianFilterLayer())
        center_column = simulator_instance.image.shape[1] // 2
        center_column_offset = int(simulator_instance.image.shape[1] * dead_detector_field_position_percent)

        simulator_instance.image[:, center_column - 40:center_column -36] = 0
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0)
        plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)


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
        simulator_instance = generate_dicom_using_layers(file_path, perfect_open_field_layers)
        

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
        simulator_instance = generate_dicom_using_layers(file_path, field_layers)

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
        simulator_instance = generate_dicom_using_layers(file_path, field_layers)

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
        simulator_instance = generate_dicom_using_layers(file_path, field_layers)

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
        simulator_instance = generate_dicom_using_layers(file_path, field_layers)

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
        simulator_instance = generate_dicom_using_layers(file_path, field_layers)


        field_layers = [
            layers.FilterFreeFieldLayer(
            field_size_mm=(100, 100), 
            alpha=1.0, 
            cax_offset_mm=(0, 0)), 
            layers.GaussianFilterLayer()
            ]

        file_path = dir_path / "flatness_imperfect_fff_10x10.dcm"
        simulator_instance = generate_dicom_using_layers(file_path, field_layers)

