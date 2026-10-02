from pathlib import Path

from pylinac.core.image_generator import AS1200Image
from pylinac.core.image_generator.simulators import Simulator

from .base import BaseImageGenerator
from . import artifacts, profiles, winston_lutz


class ImageGenerator(BaseImageGenerator):
    """
    Generates the FauxPID test images. Each generate_*_images method writes one folder of images;
    the image definitions live in artifacts.py, profiles.py and winston_lutz.py.
    """
    def __init__(
            self, 
            file_out_directory : Path, 
            simulator: type[Simulator] = AS1200Image, 
            sid=1000, 
            include_png: bool = True
            ):
        super().__init__(file_out_directory, simulator=simulator, sid=sid, include_png=include_png)

    def generate_artifacts_images(self, dead_detector_field_position_percent : float = 30.0):
        artifacts.generate_artifacts_images(self, dead_detector_field_position_percent)

    def generate_cax_offset_images(self):
        profiles.generate_cax_offset_images(self)

    def generate_field_size_images(self):
        profiles.generate_field_size_images(self)

    def generate_flatness_images(self):
        profiles.generate_flatness_images(self)

    def generate_symmetry_images(self):
        profiles.generate_symmetry_images(self)

    def generate_penumbra_images(self):
        profiles.generate_penumbra_images(self)

    def generate_winston_lutz_images(self):
        winston_lutz.generate_winston_lutz_images(self)
