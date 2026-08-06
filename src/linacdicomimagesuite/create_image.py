
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
    def __init__(
            self, 
            file_out_directory : Path, 
            simulator: type[Simulator] = AS1200Image, 
            sid=1000, 
            include_png: bool = True
            ):
        self.file_out_directory = file_out_directory
        self.sid = sid
        self.simulator = simulator
        self.include_png = include_png

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
        if self.include_png:
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

        #TODO: Use negative alpha values to subtract to simplify image generation
        file_path = dir_path / "artifact_detector_decrease_10x10.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
            field_size_mm=(100, 100)
        ))
        subtractimage = self.simulator(sid=self.sid)
        subtractimage.add_layer(layers.PerfectFieldLayer(
            field_size_mm=(5, 5),
            cax_offset_mm=(0, 10)
            #alpha=-0.1
        ))
        simulator_instance.image = simulator_instance.image - 0.1 * subtractimage.image
        simulator_instance.add_layer(layers.GaussianFilterLayer())
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        #TODO: Use positive alpha values to add to simplify image generation
        file_path = dir_path / "artifact_detector_increase_10x10.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
            field_size_mm=(100, 100)
        ))
        addimage = self.simulator(sid=self.sid)
        addimage.add_layer(layers.PerfectFieldLayer(
            field_size_mm=(5, 5),
            cax_offset_mm=(0, 10)
            #alpha=0.1
        ))
        simulator_instance.image = simulator_instance.image + 0.1 * addimage.image
        simulator_instance.add_layer(layers.GaussianFilterLayer())
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        #TODO: Use positive alpha values to add to simplify image generation
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
        if self.include_png:
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
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

    def generate_cax_offset_images(self):
        dir_path = self.file_out_directory / "CAX Offset"
        dir_path.mkdir(parents=True, exist_ok=True)

        file_path = dir_path / "cax_offset_10_mm_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.9,
            cax_offset_mm=(0, 10)
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "cax_offset_5_mm_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.9,
            cax_offset_mm=(0, 5)
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "cax_offset_1_mm_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.9,
            cax_offset_mm=(0, 1)
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "cax_offset_minus_3_mm_x_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.9,
            cax_offset_mm=(0, -3)
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "cax_offset_minus_1_mm_y_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.9,
            cax_offset_mm=(-1, 0)
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "cax_offset_5_mm_y_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.9,
            cax_offset_mm=(5, 0)
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

        file_path = dir_path / "cax_offset_7_mm_x_and_y_10x10.dcm"
        field_layers = [
        layers.FilteredFieldLayer(
            field_size_mm=(100, 100),
            alpha=0.9,
            cax_offset_mm=(7, 7)
        ),
        layers.GaussianFilterLayer()
        ]
        self.generate_dicom_using_layers(file_path, field_layers)

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

    def generate_winston_lutz_images(self):
        """
        Generates DICOM files with Winston-Lutz variations at the specified directory path.
        Note that the results are sensitive to the SID and pixel size due to the way the slope layer modifies the image. 
        """
        dir_path = self.file_out_directory / "Winston-Lutz"
        dir_path.mkdir(parents=True, exist_ok=True)

        dir_perfect = dir_path / "perfect"
        dir_perfect.mkdir(parents=True, exist_ok=True)

        file_path = dir_perfect / "winston_lutz_perfect_coll_000.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_coll_045.dcm" #Using add layer because rotations are not supported
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 45, reshape=False, mode='nearest')
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=45.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_perfect / "winston_lutz_perfect_coll_090.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 45, reshape=False, mode='nearest')
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=90.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_perfect / "winston_lutz_perfect_coll_135.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 45, reshape=False, mode='nearest')
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=135.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_perfect / "winston_lutz_perfect_coll_225.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 45, reshape=False, mode='nearest')
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=225.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_perfect / "winston_lutz_perfect_coll_270.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 45, reshape=False, mode='nearest')
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=270.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_perfect / "winston_lutz_perfect_coll_315.dcm"
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 45, reshape=False, mode='nearest')
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=315.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_perfect / "winston_lutz_perfect_couch_000.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_couch_045.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=45.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_couch_090.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=90.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_couch_270.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=270.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_couch_315.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=315.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_gantry_000.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_gantry_045.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=45.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_gantry_090.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=90.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_gantry_135.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=135.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_gantry_180.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=180.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_gantry_225.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=225.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_gantry_270.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=270.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_perfect / "winston_lutz_perfect_gantry_315.dcm"
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=315.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        dir_1mm_right = dir_path / "1mm_right"
        dir_1mm_right.mkdir(parents=True, exist_ok=True)

        file_path = dir_1mm_right / "winston_lutz_1mm_right_coll_000.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0, 1)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_coll_045.dcm" #Using add layer because rotations are not supported
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 45, reshape=False, mode='nearest')
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0, 1)))
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=45.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_1mm_right / "winston_lutz_1mm_right_coll_090.dcm" #Using add layer because rotations are not supported
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 90, reshape=False, mode='nearest')
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0, 1)))
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=90.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_1mm_right / "winston_lutz_1mm_right_coll_135.dcm" #Using add layer because rotations are not supported
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 135, reshape=False, mode='nearest')
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0, 1)))
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=135.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_1mm_right / "winston_lutz_1mm_right_coll_225.dcm" #Using add layer because rotations are not supported
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 225, reshape=False, mode='nearest')
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0, 1)))
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=225.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_1mm_right / "winston_lutz_1mm_right_coll_270.dcm" #Using add layer because rotations are not supported
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 270, reshape=False, mode='nearest')
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0, 1)))
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=270.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_1mm_right / "winston_lutz_1mm_right_coll_315.dcm" #Using add layer because rotations are not supported
        simulator_instance = self.simulator(sid=self.sid)
        simulator_instance.add_layer(layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)))
        simulator_instance.add_layer(layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)))
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            simulator_instance.add_layer(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        simulator_instance.image = ndimage.rotate(simulator_instance.image, 315, reshape=False, mode='nearest')
        simulator_instance.add_layer(layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0, 1)))
        simulator_instance.add_layer(layers.RandomNoiseLayer())
        simulator_instance.add_layer(layers.GaussianFilterLayer(sigma_mm=2))
        simulator_instance.generate_dicom(file_out_name=file_path, gantry_angle=0)
        add_metadata(file_path, gantry_angle=0.0, beam_limiting_device_angle=315.0, patient_support_angle=0.0)
        if self.include_png:
            plt.imsave(file_path.with_suffix('.png'), simulator_instance.image)

        file_path = dir_1mm_right / "winston_lutz_1mm_right_couch_000.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0, 1)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_couch_045.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(-0.707, 0.707)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=45.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_couch_090.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(-1.0, 0.0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=90.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_couch_270.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(1.0, 0.0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=270.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_couch_315.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.707, 0.707)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=315.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_couch_315.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.707, 0.707)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=315.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_gantry_000.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.0, 1.0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=0.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_gantry_045.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.0, 0.707)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=45.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_gantry_090.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.0, 0.0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=90.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_gantry_135.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.0, -0.707)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=135.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_gantry_180.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.0, -1.0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=45.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_gantry_225.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.0, -0.707)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=45.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_gantry_270.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.0, 0.0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=270.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        file_path = dir_1mm_right / "winston_lutz_1mm_right_gantry_315.dcm"
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(50, 50),
                alpha=0.9,
                cax_offset_mm=(0, 0)
            ),
            layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=(0.0, 0.707)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
            layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
        ]
        initial_offset = 25
        for i in range(0, 8):
            step_size = 7
            offset = (initial_offset + i * step_size, 0)
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=offset
                )
            )
            field_layers.append(
                layers.PerfectBBLayer(
                    bb_size_mm=3,
                    alpha=0.5,
                    cax_offset_mm=(-1 * offset[0], offset[1])
                )
            )
        field_layers.append(layers.RandomNoiseLayer())
        field_layers.append(layers.GaussianFilterLayer(sigma_mm=2))
        self.generate_dicom_using_layers(
            file_path, 
            field_layers, 
            gantry_angle=315.0, 
            beam_limiting_device_angle=0.0, 
            patient_support_angle=0.0, 
        )

        

