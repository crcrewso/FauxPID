"""
Winston-Lutz image generation.

Every image is the same 50x50 field with collimator markers (two thin bars and a row of small BBs along one
axis), plus a 6 mm BB whose projected offset depends on the scenario and the gantry/collimator/couch angle.
Each scenario is one dataset folder containing images at every collimator, couch and gantry angle.

Collimator rotations are simulated by rotating the field and markers with ndimage.rotate, since pylinac's
layers do not support rotation. The BB is added after that rotation so it stays fixed in the room.

Coordinate conventions
----------------------
BB position in the room, in mm from isocentre, with the gantry, collimator and couch all at 0 degrees:

    x: positive to the right, looking at the gantry from the foot of the couch
    y: positive towards the gantry ("in"); negative is away from the gantry ("out")
    z: positive towards the ceiling ("up")

Projected BB offset in the image (the cax_offset_mm passed to pylinac), in mm at isocentre:

    (down, right) - the first value moves the BB down the image (towards larger row numbers), the second
    moves it right (towards larger column numbers). At gantry 0, down in the image is "out" (away from
    the gantry), so a room position (x, y, z) projects to (-y, x).

Folder naming
-------------
A scenario where the BB is simply displaced is named <distance>mm_<direction>, using:

    right / left - along +x / -x
    in / out     - along +y / -y (towards / away from the gantry)
    up / down    - along +z / -z (towards the ceiling / floor)

For example "1mm_out" is 1 mm away from the gantry, and "1.5mm_in" would be 1.5 mm closer to the gantry.
Scenarios that aren't a single displacement (e.g. "wobble") get a descriptive name.

Adding a scenario
-----------------
Copy SAMPLE_SCENARIO below, give it a folder name and description, and add it to SCENARIOS.
WinstonLutzScenario.from_bb_position() calculates the projected offset for every angle from a BB position,
so a displaced BB needs no hand-calculated tables. For scenarios where the BB moves between images (like
"wobble"), write the coll/couch/gantry tables by hand.
"""
from dataclasses import dataclass
import math

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
    One dataset folder of Winston-Lutz images.

    folder:       Folder name under Images/Winston-Lutz/ (see "Folder naming" in the module docstring).
    description:  What the scenario simulates, in plain language.
    file_prefix:  Start of every file name; files are named <file_prefix>_<coll|couch|gantry>_<angle>.dcm.
    coll, couch, gantry:
                  angle -> projected BB offset (down, right) in mm. One image is generated per entry.
                  Only one axis is rotated per image; the other two angles are 0.
    """
    folder: str
    description: str
    file_prefix: str
    coll: dict[int, Offset]
    couch: dict[int, Offset]
    gantry: dict[int, Offset]
    # If True, the whole image (BB, noise and blur included) is rotated for collimator angles
    # instead of only the field and markers. Only used by the original "perfect" set, where the BB is centred.
    rotate_after_blur: bool = False

    @classmethod
    def from_bb_position(
            cls,
            folder: str,
            description: str,
            bb_position_mm: tuple[float, float, float],
            file_prefix: str | None = None,
            coll_angles=COLL_ANGLES,
            couch_angles=COUCH_ANGLES,
            gantry_angles=GANTRY_ANGLES,
            ):
        """
        Builds a scenario for a BB fixed at bb_position_mm = (x, y, z) in room coordinates (see the module docstring).

        Collimator rotation does not move the BB. Couch rotation (counter-clockwise viewed from above) rotates
        the BB about the vertical axis. Gantry rotation is treated as rotating the BB about the y axis, leaving
        y unchanged. Beam divergence is ignored: for offsets of a few mm it changes the projection by well under
        a pixel (see docs/IMAGEOPTIONS.md). Offsets are rounded to 3 decimals.
        """
        x, y, z = bb_position_mm

        def projected(x_mm, y_mm) -> Offset:
            return (round(-y_mm, 3) + 0.0, round(x_mm, 3) + 0.0)  # + 0.0 turns -0.0 into 0.0

        couch = {}
        for angle in couch_angles:
            t = math.radians(angle)
            couch[angle] = projected(x * math.cos(t) - y * math.sin(t), x * math.sin(t) + y * math.cos(t))
        gantry = {}
        for angle in gantry_angles:
            t = math.radians(angle)
            gantry[angle] = projected(x * math.cos(t) + z * math.sin(t), y)
        return cls(
            folder=folder,
            description=description,
            file_prefix=file_prefix or f"winston_lutz_{folder}",
            coll={angle: projected(x, y) for angle in coll_angles},
            couch=couch,
            gantry=gantry,
        )


def _same_offset(offset: Offset, angles) -> dict[int, Offset]:
    return {angle: offset for angle in angles}


# A documented template for new scenarios. It is not in SCENARIOS, so it is not generated.
# To use it, copy it into SCENARIOS and change the folder, description and BB position.
SAMPLE_SCENARIO = WinstonLutzScenario.from_bb_position(
    folder="1.5mm_in",
    description="BB 1.5 mm closer to the gantry (in), at room position (0, 1.5, 0). It projects 1.5 mm up the "
                "image at every collimator and gantry angle, and moves with the couch as the couch rotates.",
    bb_position_mm=(0, 1.5, 0),
)

# Where a scenario has a fixed BB position, from_bb_position() reproduces its table exactly (checked in
# tests/test_images.py). The tables are kept written out so each image's offset can be read at a glance.
SCENARIOS = [
    WinstonLutzScenario(
        folder="perfect",
        description="BB exactly at isocentre, room position (0, 0, 0). The BB is centred in every image; "
                    "only the collimator markers change.",
        file_prefix="winston_lutz_perfect",
        coll=_same_offset((0, 0), COLL_ANGLES),
        couch=_same_offset((0, 0), COUCH_ANGLES),
        gantry=_same_offset((0, 0), GANTRY_ANGLES),
        rotate_after_blur=True,
    ),
    WinstonLutzScenario(
        folder="1mm_right",
        description="BB 1 mm to the right, room position (1, 0, 0). The offset disappears in the projection at "
                    "gantry 90 and 270, where the beam is parallel to x.",
        file_prefix="winston_lutz_1mm_right",
        coll=_same_offset((0, 1), COLL_ANGLES),
        couch={0: (0, 1), 45: (-0.707, 0.707), 90: (-1.0, 0.0), 270: (1.0, 0.0), 315: (0.707, 0.707)},
        gantry={0: (0.0, 1.0), 45: (0.0, 0.707), 90: (0.0, 0.0), 135: (0.0, -0.707), 180: (0.0, -1.0),
                225: (0.0, -0.707), 270: (0.0, 0.0), 315: (0.0, 0.707)},
    ),
    WinstonLutzScenario(
        folder="1mm_out",
        description="BB 1 mm away from the gantry (out), room position (0, -1, 0). Gantry rotation does not "
                    "change the projection, since y is the gantry rotation axis.",
        file_prefix="winston_lutz_1mm_out",
        coll=_same_offset((1, 0), COLL_ANGLES),
        couch={0: (1, 0), 45: (0.707, 0.707), 90: (0, 1), 270: (0, -1), 315: (0.707, -0.707)},
        gantry=_same_offset((1, 0), GANTRY_ANGLES),
    ),
    WinstonLutzScenario(
        folder="complex (2, 3, 6)",
        description="BB displaced in all three directions, room position (2, 3, 6): 2 mm right, 3 mm in and "
                    "6 mm up, about 7 mm from isocentre.",
        file_prefix="winston_lutz_complex",
        coll=_same_offset((-3, 2), COLL_ANGLES),
        couch={0: (-3, 2), 45: (-3.536, -0.707), 90: (-2, -3), 270: (2, 3), 315: (-0.707, 3.536)},
        gantry={0: (-3, 2), 45: (-3, 5.657), 90: (-3, 6), 135: (-3, 2.828), 180: (-3, -2),
                225: (-3, -5.657), 270: (-3, -6), 315: (-3, -2.828)},
    ),
    WinstonLutzScenario(
        folder="wobble",
        description="Same BB position as 'complex (2, 3, 6)', but the BB moves by about 1 mm between images, "
                    "so the positions are inconsistent from image to image. Tables are hand-written.",
        file_prefix="winston_lutz_wobble",
        coll={0: (-3.707, 2.293), 45: (-3, 2), 90: (-3.707, 2.707), 135: (-3, 3), 225: (-3, 1),
              270: (-2.03, 2.21), 315: (-3.5, 2.866)},
        couch={0: (-2, 2), 45: (-4.536, -0.707), 90: (-2.707, -3.707), 270: (2, 2), 315: (-0.707, 4.536)},
        gantry={0: (-3, 2), 45: (-3.21, 6.634), 90: (-2, 6), 135: (-4, 2.828), 180: (-3, -1),
                225: (-2.293, -5.05), 270: (-3, -5), 315: (-3, -1.828)},
    ),
    WinstonLutzScenario(
        folder="outlier",
        description="Same as 'complex (2, 3, 6)' except one image: at gantry 315 the BB is projected 5 mm "
                    "further down the image (out), so that image disagrees with the rest of the set.",
        file_prefix="winston_lutz_outlier",
        coll=_same_offset((-3, 2), COLL_ANGLES),
        couch={0: (-3, 2), 45: (-3.536, -0.707), 90: (-2, -3), 270: (2, 3), 315: (-0.707, 3.536)},
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
