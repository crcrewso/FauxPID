"""
Winston-Lutz image generation.

Every image is the same 50x50 field with collimator markers (two thin bars and a row of small BBs along one
axis), plus a 6 mm BB whose projected offset depends on the scenario and the gantry/collimator/couch angle.

Collimator rotations are simulated by rotating the field and markers with ndimage.rotate, since pylinac's
layers do not support rotation. The BB is added after that rotation so it stays fixed in the room.
"""
from dataclasses import dataclass

import pylinac.core.image_generator.layers as layers
from scipy import ndimage

from .base import BaseImageGenerator

COLL_ANGLES = (0, 45, 90, 135, 225, 270, 315)
COUCH_ANGLES = (0, 45, 90, 270, 315)
GANTRY_ANGLES = (0, 45, 90, 135, 180, 225, 270, 315)

Offset = tuple[float, float]


@dataclass
class WinstonLutzScenario:
    """
    One folder of Winston-Lutz images. Each mapping is angle -> projected BB offset (cax_offset_mm) in mm.
    Images are generated for every angle listed in each mapping.
    """
    folder: str
    file_prefix: str
    coll: dict[int, Offset]
    couch: dict[int, Offset]
    gantry: dict[int, Offset]
    # If True, the whole image (BB, noise and blur included) is rotated for collimator angles
    # instead of only the field and markers. Only used by the original "perfect" set, where the BB is centred.
    rotate_after_blur: bool = False


def _same_offset(offset: Offset, angles) -> dict[int, Offset]:
    return {angle: offset for angle in angles}


SCENARIOS = [
    WinstonLutzScenario(
        folder="perfect",
        file_prefix="winston_lutz_perfect",
        coll=_same_offset((0, 0), COLL_ANGLES),
        couch=_same_offset((0, 0), COUCH_ANGLES),
        gantry=_same_offset((0, 0), GANTRY_ANGLES),
        rotate_after_blur=True,
    ),
    WinstonLutzScenario(
        folder="1mm_right",
        file_prefix="winston_lutz_1mm_right",
        coll=_same_offset((0, 1), COLL_ANGLES),
        couch={0: (0, 1), 45: (-0.707, 0.707), 90: (-1.0, 0.0), 270: (1.0, 0.0), 315: (0.707, 0.707)},
        gantry={0: (0.0, 1.0), 45: (0.0, 0.707), 90: (0.0, 0.0), 135: (0.0, -0.707), 180: (0.0, -1.0),
                225: (0.0, -0.707), 270: (0.0, 0.0), 315: (0.0, 0.707)},
    ),
    WinstonLutzScenario(
        folder="1mm_out",
        file_prefix="winston_lutz_1mm_out",
        coll=_same_offset((1, 0), COLL_ANGLES),
        couch={0: (1, 0), 45: (0.707, 0.707), 90: (0, 1), 270: (0, -1), 315: (0.707, -0.707)},
        gantry=_same_offset((1, 0), GANTRY_ANGLES),
    ),
    WinstonLutzScenario(
        folder="complex (2, 3, 6)",
        file_prefix="winston_lutz_complex",
        coll=_same_offset((-3, 2), COLL_ANGLES),
        couch={0: (-3, 2), 45: (-3.536, -0.717), 90: (-2, -3), 270: (2, 3), 315: (-0.717, 3.536)},
        gantry={0: (-3, 2), 45: (-3, 5.657), 90: (-3, 6), 135: (-3, 2.828), 180: (-3, -2),
                225: (-3, -5.657), 270: (-3, -6), 315: (-3, -2.828)},
    ),
    WinstonLutzScenario(
        folder="wobble",
        file_prefix="winston_lutz_wobble",
        coll={0: (-3.707, 2.293), 45: (-3, 2), 90: (-3.707, 2.707), 135: (-3, 3), 225: (-3, 1),
              270: (-2.03, 2.21), 315: (-3.5, 2.866)},
        couch={0: (-2, 2), 45: (-4.536, -0.717), 90: (-2.707, -3.707), 270: (2, 2), 315: (-0.717, 4.536)},
        gantry={0: (-3, 2), 45: (-3.21, 6.634), 90: (-2, 6), 135: (-4, 2.828), 180: (-3, -1),
                225: (-2.293, -5.05), 270: (-3, -5), 315: (-3, -1.828)},
    ),
    WinstonLutzScenario(
        folder="outlier",
        file_prefix="winston_lutz_outlier",
        coll=_same_offset((-3, 2), COLL_ANGLES),
        couch={0: (-3, 2), 45: (-3.536, -0.717), 90: (-2, -3), 270: (2, 3), 315: (-0.717, 3.536)},
        # Same as "complex" except for one outlier image at gantry 315.
        gantry={0: (-3, 2), 45: (-3, 5.657), 90: (-3, 6), 135: (-3, 2.828), 180: (-3, -2),
                225: (-3, -5.657), 270: (-3, -6), 315: (2, -2.828)},
    ),
]


def field_layers():
    """The 50x50 field."""
    return [layers.FilteredFieldLayer(field_size_mm=(50, 50), alpha=0.9, cax_offset_mm=(0, 0))]


def marker_layers(initial_offset=25, step_size=7, count=8):
    """Collimator markers: two thin bars and pairs of small BBs along the x axis, used to see collimator rotation."""
    markers = [
        layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(53, 0)),
        layers.PerfectFieldLayer(field_size_mm=(56, 2), alpha=0.5, cax_offset_mm=(-53, 0)),
    ]
    for i in range(count):
        offset = initial_offset + i * step_size
        markers.append(layers.PerfectBBLayer(bb_size_mm=3, alpha=0.5, cax_offset_mm=(offset, 0)))
        markers.append(layers.PerfectBBLayer(bb_size_mm=3, alpha=0.5, cax_offset_mm=(-offset, 0)))
    return markers


def bb_layer(offset: Offset):
    """The 6 mm BB at the given projected offset from the CAX."""
    return layers.PerfectBBLayer(alpha=-0.5, bb_size_mm=6, cax_offset_mm=offset)


def finishing_layers():
    """Detector noise and blur applied to every image."""
    return [layers.RandomNoiseLayer(), layers.GaussianFilterLayer(sigma_mm=2)]


def rotate(simulator_instance, angle):
    simulator_instance.image = ndimage.rotate(simulator_instance.image, angle, reshape=False, mode='nearest')


def generate_winston_lutz_image(
        generator: BaseImageGenerator,
        file_path,
        bb_offset: Offset,
        gantry_angle: float = 0.0,
        coll_angle: float = 0.0,
        couch_angle: float = 0.0,
        rotate_after_blur: bool = False,
        ):
    """
    Generates one Winston-Lutz image. coll_angle rotates the field and markers in the image;
    gantry_angle and couch_angle are only written to the metadata (bb_offset should already include their effect).
    """
    simulator_instance = generator.new_simulator(field_layers())
    if rotate_after_blur:
        for layer in [bb_layer(bb_offset), *marker_layers(), *finishing_layers()]:
            simulator_instance.add_layer(layer)
        if coll_angle:
            rotate(simulator_instance, coll_angle)
    else:
        for layer in marker_layers():
            simulator_instance.add_layer(layer)
        if coll_angle:
            rotate(simulator_instance, coll_angle)
        for layer in [bb_layer(bb_offset), *finishing_layers()]:
            simulator_instance.add_layer(layer)
    generator.save(simulator_instance, file_path, {
        "gantry_angle": float(gantry_angle),
        "beam_limiting_device_angle": float(coll_angle),
        "patient_support_angle": float(couch_angle),
    })


def generate_winston_lutz_images(generator: BaseImageGenerator):
    """
    Generates DICOM files with Winston-Lutz variations at the specified directory path.
    Note that the results are sensitive to the SID and pixel size due to the way the slope layer modifies the image.
    """
    for scenario in SCENARIOS:
        dir_path = generator.output_dir("Winston-Lutz", scenario.folder)
        axes = (
            ("coll", scenario.coll, "coll_angle"),
            ("couch", scenario.couch, "couch_angle"),
            ("gantry", scenario.gantry, "gantry_angle"),
        )
        for axis_name, offsets, angle_kwarg in axes:
            for angle, bb_offset in offsets.items():
                generate_winston_lutz_image(
                    generator,
                    dir_path / f"{scenario.file_prefix}_{axis_name}_{angle:03d}.dcm",
                    bb_offset,
                    rotate_after_blur=scenario.rotate_after_blur,
                    **{angle_kwarg: angle},
                )
