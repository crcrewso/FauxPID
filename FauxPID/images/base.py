from pathlib import Path

from matplotlib import pyplot as plt

from pylinac.core.image_generator import AS1200Image
from pylinac.core.image_generator.simulators import Simulator
from ..utils.dicom_metadata import add_metadata


class BaseImageGenerator:
    """
    Shared plumbing for the image generators: creating simulators, output folders and saving DICOM/PNG files.
    The generator functions in the other modules of this package take an instance of this class.
    """
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

    def new_simulator(self, layers=()) -> Simulator:
        """Creates a simulator at this generator's SID and applies the given layers in order."""
        simulator_instance = self.simulator(sid=self.sid)
        for layer in layers:
            simulator_instance.add_layer(layer)
        return simulator_instance

    def output_dir(self, *parts: str) -> Path:
        """Returns (and creates) a folder under the output directory, e.g. output_dir("Winston-Lutz", "perfect")."""
        dir_path = self.file_out_directory.joinpath(*parts)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    def save(self, simulator_instance: Simulator, file_out_name: Path, metadata: dict | None = None):
        """
        Writes the simulator's image to a DICOM file, then updates its metadata using add_metadata.
        Pass metadata=None to skip the metadata update. Also saves a PNG version for reference if enabled.
        """
        simulator_instance.generate_dicom(file_out_name=file_out_name, gantry_angle=0)
        if metadata is not None:
            add_metadata(file_out_name, **metadata)
        if self.include_png:
            plt.imsave(file_out_name.with_suffix('.png'), simulator_instance.image)

    def generate_dicom_using_layers(self, file_out_name, layers, **metadata_kwargs):
        """
        Generates a DICOM file using the specified layers and saves it to the specified file_out_name.
        Updates the metadata of the DICOM file using the add_metadata function. Also saves a PNG version of the image
        in the same directory for reference.
        """
        simulator_instance = self.new_simulator(layers)
        self.save(simulator_instance, file_out_name, metadata_kwargs)
        return simulator_instance
