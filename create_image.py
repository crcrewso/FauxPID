
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

    def generate_dicom_using_layers(self, file_out_name, layers, **metadata_kwargs):
        """
        Generates a DICOM file using the specified layers and saves it to the specified file_out_name. 
        Updates the metadata of the DICOM file using the add_metadata function. Also saves a PNG version of the image
        in the same directory for reference.
        """
        simulator_instance = self.simulator(sid=self.sid)
        for layer in layers:
            simulator_instance.add_layer(layer)
        simulator_instance.generate_dicom(file_out_name=file_out_name, gantry_angle=0)
        add_metadata(file_out_name, **metadata_kwargs)
        plt.imsave(file_out_name.with_suffix('.png'), simulator_instance.image)
        return simulator_instance

    def generate_artifacts_images(self, dead_detector_field_position_percent : float = 30.0):
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
        field_size = 100 # in mm
        simulator_instance.add_layer(layers.FilteredFieldLayer(
            field_size_mm=(field_size, field_size)
        ))
        simulator_instance.add_layer(layers.GaussianFilterLayer())
        center_column = simulator_instance.image.shape[1] // 2
        dpmm = 1 / simulator_instance.pixel_size
        left_field_offset = int(field_size * dpmm * dead_detector_field_position_percent / 100)
        center_column_offset = center_column + left_field_offset
        simulator_instance.image[:, center_column_offset: center_column_offset + 4] = 0
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0)
        plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

    def generate_field_size_images(self):
        dir_path = self.file_out_directory / "Field Size"
        dir_path.mkdir(parents=True, exist_ok=True)

        file_path = dir_path / "field_size_perfect_10x10.dcm"
        perfect_open_field_layers = [
        layers.PerfectFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, perfect_open_field_layers)

        file_path = dir_path / "field_size_realistic_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0,
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "field_size_realistic_20x20.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(200, 200), 
        alpha=1.0,
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            leaf_jaw_x_positions=[-100, 100], # Normally defaulted to [-50, 50] so need to set manually
            leaf_jaw_y_positions=[-100, 100]
        )

        file_path = dir_path / "field_size_rotated_5_degrees_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0,
        cax_offset_mm=(0, 0), 
        rotation=5), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "field_size_plus_10_mm_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 110), 
        alpha=1.0,
        cax_offset_mm=(0, 5), 
        rotation=5), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            leaf_jaw_x_positions=[-50.0, 50.0], # "Normal" metadata
            leaf_jaw_y_positions=[-50.0, 50.0]
        )

        file_path = dir_path / "field_size_plus_5_mm_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 105), 
        alpha=1.0,
        cax_offset_mm=(0, 2.5), 
        rotation=5), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            leaf_jaw_x_positions=[-50.0, 50.0], # "Normal" metadata
            leaf_jaw_y_positions=[-50.0, 50.0]
        )

        file_path = dir_path / "field_size_plus_1_mm_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 101), 
        alpha=1.0,
        cax_offset_mm=(0, 0.5), 
        rotation=5), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            leaf_jaw_x_positions=[-50.0, 50.0], # "Normal" metadata
            leaf_jaw_y_positions=[-50.0, 50.0]
        )


    def generate_flatness_images(self):
        dir_path = self.file_out_directory / "Flatness"
        dir_path.mkdir(parents=True, exist_ok=True)

        perfect_open_field_layers = [
        layers.PerfectFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        file_path = dir_path / "flatness_perfect_10x10.dcm"
        self.generate_dicom_using_layers(file_path, perfect_open_field_layers)
        

        file_path = dir_path / "flatness_excess_horns_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        gaussian_height=0.1, 
        gaussian_sigma_mm=32.0,
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "flatness_filtered_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        gaussian_height=0.03, 
        gaussian_sigma_mm=32.0,
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "flatness_two_percent_variance_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        gaussian_height=0.03, 
        gaussian_sigma_mm=33.968,
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "flatness_two_percent_IEC_ratio_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        gaussian_height=0.03, 
        gaussian_sigma_mm=30.92,
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "flatness_two_percent_CAX_ratio_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        gaussian_height=0.0222, 
        gaussian_sigma_mm=32,
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)


        file_path = dir_path / "flatness_imperfect_fff_10x10.dcm"
        field_layers = [
        layers.FilterFreeFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)
    
    def generate_symmetry_images(self):
        """
        Generates DICOM files with symmetry variations at the specified directory path.
        Note that the results are sensitive to the SID and pixel size due to the way the slope layer modifies the image. 
        """
        dir_path = self.file_out_directory / "Symmetry"
        dir_path.mkdir(parents=True, exist_ok=True)

        file_path = dir_path / "symmetry_perfect_10x10.dcm"
        perfect_open_field_layers = [
        layers.PerfectFieldLayer(
        field_size_mm=(100, 100), 
        alpha=1.0, 
        cax_offset_mm=(0, 0)), 
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, perfect_open_field_layers)

        file_path = dir_path / "symmetry_two_percent_x_cax_point_difference_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.5,
        ),
        layers.SlopeLayer(
            slope_x=-0.09929,
            slope_y=0.0
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "symmetry_two_percent_x_point_ratio_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.5,
        ),
        layers.SlopeLayer(
            slope_x=-0.1335,
            slope_y=0.0
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "symmetry_two_percent_x_area_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.5,
        ),
        layers.SlopeLayer(
            slope_x=0.2371,
            slope_y=0.0
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "symmetry_positive_y_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.5,
        ),
        layers.SlopeLayer(
            slope_x=0.0,
            slope_y=0.8
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "symmetry_negative_y_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.5,
        ),
        layers.SlopeLayer(
            slope_x=0.0,
            slope_y=-0.6
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "symmetry_x_and_y_gradient_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.5,
        ),
        layers.SlopeLayer(
            slope_x=0.8,
            slope_y=0.8
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)


