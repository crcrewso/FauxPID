import pylinac.core.image_generator.layers as layers

from .base import BaseImageGenerator

FIELD_SIZE_MM = 100

# (file name, patch field size in mm, patch intensity relative to the open field, write metadata)
# Each patch is a perfect field offset 10 mm from the CAX, added to (or subtracted from) a 10x10 open field.
PATCH_ARTIFACTS = [
    ("artifact_detector_decrease_10x10.dcm", (5, 5), -0.1, True),
    ("artifact_detector_increase_10x10.dcm", (5, 5), 0.1, True),
    ("artifact_vertical_bar_10x10.dcm", (100, 5), 0.5, False),
]


def generate_artifacts_images(generator: BaseImageGenerator, dead_detector_field_position_percent: float = 30.0):
    """
    Generates DICOM files with artifacts at the specified directory path.
    To make your own artifact images create a new simulator_instance, add a field layer, then modify simulator_instance.image as needed.
    The image is an array of pixel values that can be modified as needed to create the desired artifact.
    """
    dir_path = generator.output_dir("Artifacts")

    #TODO: Use alpha values on the patch layer instead of image arithmetic to simplify image generation
    for file_name, patch_size_mm, scale, write_metadata in PATCH_ARTIFACTS:
        simulator_instance = generator.new_simulator([
            layers.FilteredFieldLayer(field_size_mm=(FIELD_SIZE_MM, FIELD_SIZE_MM))
        ])
        patch = generator.new_simulator([
            layers.PerfectFieldLayer(field_size_mm=patch_size_mm, cax_offset_mm=(0, 10))
        ])
        if scale < 0:
            simulator_instance.image = simulator_instance.image - abs(scale) * patch.image
        else:
            simulator_instance.image = simulator_instance.image + scale * patch.image
        simulator_instance.add_layer(layers.GaussianFilterLayer())
        # TODO: the vertical bar image has never had its metadata updated; confirm whether that is intended.
        generator.save(simulator_instance, dir_path / file_name, {"gantry_angle": 0} if write_metadata else None)

    simulator_instance = generator.new_simulator([
        layers.FilteredFieldLayer(field_size_mm=(FIELD_SIZE_MM, FIELD_SIZE_MM)),
        layers.GaussianFilterLayer(),
    ])
    center_column = simulator_instance.image.shape[1] // 2
    dpmm = 1 / simulator_instance.pixel_size
    left_field_offset = int(FIELD_SIZE_MM * dpmm * dead_detector_field_position_percent / 100)
    center_column_offset = center_column + left_field_offset
    simulator_instance.image[:, center_column_offset: center_column_offset + 4] = 0
    generator.save(simulator_instance, dir_path / "artifact_zero_4_columns_10x10.dcm", {"gantry_angle": 0})
