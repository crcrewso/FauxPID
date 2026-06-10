from datetime import datetime, timezone
from pathlib import Path
import tomllib

import pydicom as dicom

#TODO: May break when converting to EXE, maybe turn the version into a static constant
def _load_software_version() -> str:
    """
    Gets the software version from the pyproject.toml file. If the file is not found or the version is not specified, returns "0.0.0".
    """
    pyproject_path = Path(__file__).with_name("pyproject.toml")
    try:
        with pyproject_path.open("rb") as pyproject_file:
            project_data = tomllib.load(pyproject_file)
        return project_data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "0.0.0"


PROJECT_VERSION = _load_software_version()


def add_metadata(file_name, leaf_jaw_positions=[-50.0, 50.0], gantry_angle=0.0):
    """
    Adds metadata to the DICOM file specified by file_name. 
    """
    ds = dicom.dcmread(file_name)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    
    ds.InstanceCreationDate = datetime.now().strftime('%Y%m%d')
    ds.InstanceCreationTime = datetime.now().strftime('%H%M%S')
    ds.AcquisitionDate = datetime.now().strftime('%Y%m%d')
    ds.AcquisitionTime = datetime.now().strftime('%H%M%S')

    ds.StationName = 'TDCreator'
    ds.Manufacturer = 'TDCreator'
    ds.OperatorsName = 'TDCreator'

    ds.PatientBirthDate = epoch.strftime('%Y%m%d')
    ds.PatientBirthTime = epoch.strftime('%H%M%S')

    ds.SoftwareVersions = PROJECT_VERSION

    ds.PixelRepresentation = 0
    ds.PixelIntensityRelationship = 'LIN'
    ds.PixelIntensityRelationshipSign = 1

    ds.BeamLimitingDeviceAngle = 0.0
    ds.PatientSupportAngle = 0.0

    ds.TableTopVerticalPosition = 0.0
    ds.TableTopLongitudinalPosition = 20.0
    ds.TableTopLateralPosition = 0.0
    ds.TableTopPitchAngle = 0.0
    ds.TableTopRollAngle = 0.0

    exposure_dataset = dicom.Dataset()
    exposure_dataset.KVP = 6000.0
    exposure_dataset.ExposureTime = 1
    exposure_dataset.MetersetExposure = 100

    beam_limiting_device_dataset = dicom.Dataset()
    beam_limiting_device_dataset.LeafJawPositions = leaf_jaw_positions
    exposure_dataset.GantryAngle = gantry_angle
    exposure_dataset.TableTopVerticalPosition = ds.TableTopVerticalPosition
    exposure_dataset.TableTopLongitudinalPosition = ds.TableTopLongitudinalPosition
    exposure_dataset.TableTopLateralPosition = ds.TableTopLateralPosition
    exposure_dataset.TableTopPitchAngle = ds.TableTopPitchAngle
    exposure_dataset.TableTopRollAngle = ds.TableTopRollAngle
    exposure_dataset.BeamLimitingDeviceSequence = dicom.Sequence([beam_limiting_device_dataset])

    ds.ExposureSequence = dicom.Sequence([exposure_dataset])
    ds.IsocenterPosition = [0.0, 0.0, 0.0]

    ds.save_as(file_name)