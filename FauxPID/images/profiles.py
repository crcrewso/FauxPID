"""
Generators for profile-based images: CAX offset, field size, flatness, symmetry and penumbra.
Each image is a list of pylinac layers; the tables below list what makes each image different.
"""
import pylinac.core.image_generator.layers as layers

from .base import BaseImageGenerator

# "Normal" jaw metadata for a 10x10 field. add_metadata defaults to this as well.
JAWS_10X10 = {"leaf_jaw_x_positions": [-50.0, 50.0], "leaf_jaw_y_positions": [-50.0, 50.0]}


def perfect_field_layers(field_size_mm=(100, 100)):
    """A perfectly flat field with a default Gaussian blur."""
    return [
        layers.PerfectFieldLayer(field_size_mm=field_size_mm, alpha=1.0, cax_offset_mm=(0, 0)),
        layers.GaussianFilterLayer(),
    ]


def filtered_field_layers(field_size_mm=(100, 100), alpha=1.0, cax_offset_mm=(0, 0), sigma_mm=None, **field_kwargs):
    """
    A realistic (filtered) field followed by a Gaussian blur.
    sigma_mm sets the blur width; None uses pylinac's default. field_kwargs go to FilteredFieldLayer
    (e.g. gaussian_height, gaussian_sigma_mm, rotation).
    """
    blur = layers.GaussianFilterLayer() if sigma_mm is None else layers.GaussianFilterLayer(sigma_mm=sigma_mm)
    return [
        layers.FilteredFieldLayer(field_size_mm=field_size_mm, alpha=alpha, cax_offset_mm=cax_offset_mm, **field_kwargs),
        blur,
    ]


def sloped_field_layers(slope_x, slope_y):
    """A half-intensity filtered field with a linear gradient, used to create asymmetric profiles."""
    return [
        layers.FilteredFieldLayer(field_size_mm=(100, 100), alpha=0.5),
        layers.SlopeLayer(slope_x=slope_x, slope_y=slope_y),
        layers.GaussianFilterLayer(),
    ]


# file name -> CAX offset in mm
CAX_OFFSETS = {
    "cax_offset_10_mm_10x10.dcm": (0, 10),
    "cax_offset_5_mm_10x10.dcm": (0, 5),
    "cax_offset_1_mm_10x10.dcm": (0, 1),
    "cax_offset_minus_3_mm_x_10x10.dcm": (0, -3),
    "cax_offset_minus_1_mm_y_10x10.dcm": (-1, 0),
    "cax_offset_5_mm_y_10x10.dcm": (5, 0),
    "cax_offset_7_mm_x_and_y_10x10.dcm": (7, 7),
}


def generate_cax_offset_images(generator: BaseImageGenerator):
    dir_path = generator.output_dir("CAX Offset")
    for file_name, offset in CAX_OFFSETS.items():
        generator.generate_dicom_using_layers(
            dir_path / file_name, filtered_field_layers(alpha=0.9, cax_offset_mm=offset)
        )


def generate_field_size_images(generator: BaseImageGenerator):
    dir_path = generator.output_dir("Field Size")

    generator.generate_dicom_using_layers(dir_path / "field_size_perfect_10x10.dcm", perfect_field_layers())
    generator.generate_dicom_using_layers(dir_path / "field_size_realistic_10x10.dcm", filtered_field_layers())
    generator.generate_dicom_using_layers(
        dir_path / "field_size_realistic_20x20.dcm",
        filtered_field_layers(field_size_mm=(200, 200)),
        leaf_jaw_x_positions=[-100, 100], # Normally defaulted to [-50, 50] so need to set manually
        leaf_jaw_y_positions=[-100, 100],
    )
    generator.generate_dicom_using_layers(
        dir_path / "field_size_rotated_5_degrees_10x10.dcm", filtered_field_layers(rotation=5)
    )

    # Fields larger than the 10x10 the metadata reports. The extra size is added on one side only,
    # so the CAX offset is half of it.
    for extra_mm, file_label in ((10, "10"), (5, "5"), (1, "1")):
        generator.generate_dicom_using_layers(
            dir_path / f"field_size_plus_{file_label}_mm_10x10.dcm",
            filtered_field_layers(field_size_mm=(100, 100 + extra_mm), cax_offset_mm=(0, extra_mm / 2), rotation=5),
            **JAWS_10X10,
        )


# file name -> (gaussian_height, gaussian_sigma_mm) of the filtered field "horns"
FLATNESS_HORNS = {
    "flatness_excess_horns_10x10.dcm": (0.1, 32.0),
    "flatness_filtered_10x10.dcm": (0.03, 32.0),
    "flatness_two_percent_variance_10x10.dcm": (0.03, 33.968),
    "flatness_two_percent_IEC_ratio_10x10.dcm": (0.03, 30.92),
    "flatness_two_percent_CAX_ratio_10x10.dcm": (0.0222, 32),
}


def generate_flatness_images(generator: BaseImageGenerator):
    dir_path = generator.output_dir("Flatness")

    generator.generate_dicom_using_layers(dir_path / "flatness_perfect_10x10.dcm", perfect_field_layers())
    for file_name, (height, sigma) in FLATNESS_HORNS.items():
        generator.generate_dicom_using_layers(
            dir_path / file_name, filtered_field_layers(gaussian_height=height, gaussian_sigma_mm=sigma)
        )
    generator.generate_dicom_using_layers(
        dir_path / "flatness_imperfect_fff_10x10.dcm",
        [
            layers.FilterFreeFieldLayer(field_size_mm=(100, 100), alpha=1.0, cax_offset_mm=(0, 0)),
            layers.GaussianFilterLayer(),
        ],
    )


# file name -> (slope_x, slope_y)
SYMMETRY_SLOPES = {
    "symmetry_two_percent_x_cax_point_difference_10x10.dcm": (-0.09929, 0.0),
    "symmetry_two_percent_x_point_ratio_10x10.dcm": (-0.1335, 0.0),
    "symmetry_two_percent_x_area_10x10.dcm": (0.2371, 0.0),
    "symmetry_positive_y_10x10.dcm": (0.0, 0.8),
    "symmetry_negative_y_10x10.dcm": (0.0, -0.6),
    "symmetry_x_and_y_gradient_10x10.dcm": (0.8, 0.8),
}


def generate_symmetry_images(generator: BaseImageGenerator):
    """
    Generates DICOM files with symmetry variations at the specified directory path.
    Note that the results are sensitive to the SID and pixel size due to the way the slope layer modifies the image.
    """
    dir_path = generator.output_dir("Symmetry")

    generator.generate_dicom_using_layers(dir_path / "symmetry_perfect_10x10.dcm", perfect_field_layers())
    for file_name, (slope_x, slope_y) in SYMMETRY_SLOPES.items():
        generator.generate_dicom_using_layers(dir_path / file_name, sloped_field_layers(slope_x, slope_y))


# file name -> Gaussian blur sigma in mm (None means no blur)
PENUMBRA_BLUR = {
    "penumbra_perfect.dcm": None,
    "penumbra_realistic.dcm": 2,
    "penumbra_1_mm.dcm": 0.6,
    "penumbra_2_mm.dcm": 1.2,
    "penumbra_10_mm.dcm": 6.0,
}


def generate_penumbra_images(generator: BaseImageGenerator):
    """
    Generates DICOM files with penumbra variations at the specified directory path.
    """
    dir_path = generator.output_dir("Penumbra")
    for file_name, sigma in PENUMBRA_BLUR.items():
        field_layers = [
            layers.FilteredFieldLayer(
                field_size_mm=(100, 100),
                alpha=1.0,
                gaussian_height=0.1,
                gaussian_sigma_mm=32.0,
                cax_offset_mm=(0, 0)),
        ]
        if sigma is not None:
            field_layers.append(layers.GaussianFilterLayer(sigma_mm=sigma))
        generator.generate_dicom_using_layers(dir_path / file_name, field_layers)
