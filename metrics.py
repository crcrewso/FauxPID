import numpy as np
from matplotlib import pyplot as plt

import pydicom

from pylinac import FieldProfileAnalysis, Centering, Normalization, Edge
from pylinac.metrics.profile import (
    ProfileMetric,
    PenumbraLeftMetric,
    PenumbraRightMetric,
    SymmetryAreaMetric,
    FlatnessDifferenceMetric,
    FlatnessRatioMetric
)

# Finds the value of the central axis (CAX) by taking the average of the two middle values in the profile. This is a common method for finding the CAX value in a profile, as it is less sensitive to noise than taking the maximum value.
def get_cax_value(values: np.ndarray) -> float:
    length = len(values)
    return (values[length // 2] + values[length // 2 - 1]) / 2

# Finds the indices of the left and right transitions in the profile, where the values cross a specified threshold. The left transition is found by iterating from the beginning of the profile until a value greater than the threshold is found, while the right transition is found by iterating from the end of the profile until a value greater than the threshold is found. If either transition is not found, a ValueError is raised.
def get_transition_indices(values: np.ndarray, threshold: float) -> tuple[int, int]:
    length = len(values)

    print(threshold)
    print(values.max())

    left_transition = -1
    for i, val in enumerate(values):
        if val > threshold:
            left_transition = i
            break

    right_transition = -1
    for i in range(length - 1, -1, -1):
        if values[i] > threshold:
            right_transition = i
            break
    
    if left_transition == -1 or right_transition == -1:
        raise ValueError("Threshold not crossed in the profile.")
    
    return left_transition, right_transition

class FlatnessCalculationByVariance(ProfileMetric):
    name = "Flatness Calculation by Variance"
    unit = "%"

    def __init__(self, in_field_ratio: float = 0.8, color="g", linestyle="-."):
        self.in_field_ratio = in_field_ratio
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        values = self.profile.values
        cax_value = get_cax_value(values)
        fifty_percent_value = cax_value * 0.5
        cax_index = self.profile.cax_index
        left_field_index, right_field_index = get_transition_indices(values, fifty_percent_value)
        if left_field_index > cax_index or right_field_index < cax_index:
            raise ValueError("CAX index is not between the left and right field indices.")

        left_roi_index = (int) (cax_index - (cax_index - left_field_index) * self.in_field_ratio)
        right_roi_index = (int) (cax_index + (right_field_index - cax_index) * self.in_field_ratio)

        return (
            100
            * (values[left_roi_index:right_roi_index+1].max() - values[left_roi_index:right_roi_index+1].min())
            / (values[left_roi_index:right_roi_index+1].max() + values[left_roi_index:right_roi_index+1].min())
        )

class FlatnessCalculationByRatio(ProfileMetric):
    name = "Flatness Calculation by Ratio (IEC)"
    unit = "%"

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        
        values = self.profile.values
        cax_value = get_cax_value(values)
        fifty_percent_value = cax_value * 0.5
        cax_index = self.profile.cax_index
        left_field_index, right_field_index = get_transition_indices(values, fifty_percent_value)
        if left_field_index > cax_index or right_field_index < cax_index:
            raise ValueError("CAX index is not between the left and right field indices.")

        left_length_mm = (cax_index - left_field_index) / self.profile.dpmm
        right_length_mm = (right_field_index - cax_index) / self.profile.dpmm

        if left_length_mm < 100:
            left_roi_index = (int) (cax_index - (left_length_mm - 20) * self.profile.dpmm)
        elif left_length_mm < 300:
            left_roi_index = (int) (cax_index - (left_length_mm * 0.8) * self.profile.dpmm)
        else:
            left_roi_index = (int) (cax_index - (left_length_mm - 60) * self.profile.dpmm)

        if right_length_mm < 100:
            right_roi_index = (int) (cax_index + (right_length_mm - 20) * self.profile.dpmm)
        elif right_length_mm < 300:
            right_roi_index = (int) (cax_index + (right_length_mm * 0.8) * self.profile.dpmm)
        else:
            right_roi_index = (int) (cax_index + (right_length_mm - 60) * self.profile.dpmm)
        print ("left_roi_index:", left_roi_index)
        print ("right_roi_index:", right_roi_index)
        return (
            100
            * (values[left_roi_index:right_roi_index+1].max())
            / (values[left_roi_index:right_roi_index+1].min())
        )

class FlatnessCalculationByCaxVariance(ProfileMetric):
    name = "Flatness Calculation by CAX Variance"
    unit = ""

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        
        values = self.profile.values
        cax_value = get_cax_value(values)
        fifty_percent_value = cax_value * 0.5
        cax_index = self.profile.cax_index
        left_field_index, right_field_index = get_transition_indices(values, fifty_percent_value)
        if left_field_index > cax_index or right_field_index < cax_index:
            raise ValueError("CAX index is not between the left and right field indices.")

        left_roi_index = left_field_index
        right_roi_index = right_field_index
        return (
            (values[left_roi_index:right_roi_index+1].max()
            - values[left_roi_index:right_roi_index+1].min())
            / cax_value
        )

class FlatnessCalculationByCaxRatio(ProfileMetric):
    name = "Flatness Calculation by CAX Ratio"
    unit = ""

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        values = self.profile.values
        cax_value = get_cax_value(values)
        fifty_percent_value = cax_value * 0.5
        cax_index = self.profile.cax_index
        left_field_index, right_field_index = get_transition_indices(values, fifty_percent_value)
        if left_field_index > cax_index or right_field_index < cax_index:
            raise ValueError("CAX index is not between the left and right field indices.")

        left_roi_index = (int) (cax_index - (cax_index - left_field_index) * 0.9)
        right_roi_index = (int) (cax_index + (right_field_index - cax_index) * 0.9)
        return (
            (values[left_roi_index:right_roi_index+1].max())
            / cax_value
        )
    
### TESTING DELETE LATER
path = 'Solstice-m12_d18_2025-FS_EPID_MLC 10x38.dcm'
field_analyzer = FieldProfileAnalysis(path)
field_analyzer.analyze(
    centering=Centering.BEAM_CENTER,
    # x_width=0.02,
    # y_width=0.02,
    normalization=Normalization.BEAM_CENTER,
    #edge_type=Edge.FWHM,
    ground=True,
    metrics=(
        PenumbraLeftMetric(),
        PenumbraRightMetric(),
        SymmetryAreaMetric(),
        FlatnessDifferenceMetric(),
        FlatnessCalculationByVariance(),
        FlatnessRatioMetric(),
        FlatnessCalculationByRatio(), 
        FlatnessCalculationByCaxVariance(),
        FlatnessCalculationByCaxRatio()
    ),
)
print(field_analyzer.results())
field_analyzer.plot_analyzed_images()