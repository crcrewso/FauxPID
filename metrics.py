import numpy as np
from matplotlib import pyplot as plt
import math

from pylinac import FieldProfileAnalysis, Centering, Normalization, Edge
from pylinac.metrics.profile import (
    ProfileMetric,
    PenumbraLeftMetric,
    PenumbraRightMetric,
    SymmetryAreaMetric,
    FlatnessDifferenceMetric,
    FlatnessRatioMetric,
    SymmetryPointDifferenceMetric,
)

# Finds the value of the central axis (CAX) by taking the average of the two middle values in the profile. This is a common method for finding the CAX value in a profile, as it is less sensitive to noise than taking the maximum value.
def get_cax_value(values: np.ndarray) -> float:
    length = len(values)
    return (values[length // 2] + values[(length - 1) // 2]) / 2

def get_transition_indices(values: np.ndarray, threshold: float) -> tuple[int, int]:
    """
    Finds the indices of the left and right transitions in the profile, where the values cross a specified threshold. 
    The left transition is found by iterating from the beginning of the profile until a value greater than the threshold is found, and vice versa. 
    If the threshold is not crossed in the profile, a ValueError is raised.
    This is a slow operation and can be optimized in the future. 
    """
    length = len(values)

    left_transition = -1
    for i in range(length):
        if values[i] > threshold:
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


def get_field_indices(values: np.ndarray, fwxm_ratio: float = 0.5) -> tuple[int, int]:
    """
    Finds the indices of the left and right field edges in the profile default calculating using Full Width Half Max (FWHM). 
    If the CAX is not between the left and right field edges, then the half max value is calculated using the max value over the whole profile. 
    Where the edges of a region are in between indices, the indices closer to the beam center are used.
    """
    max_value = np.max(values)
    fwxm_max = max_value * fwxm_ratio
    left_index, right_index = get_transition_indices(values, fwxm_max)
    cax_index = (len(values) - 1) / 2
    if left_index < cax_index and right_index > cax_index:
        cax_value = get_cax_value(values)
        fifty_percent_cax = cax_value * fwxm_ratio
        left_index, right_index = get_transition_indices(values, fifty_percent_cax)

    return left_index, right_index

class FieldsizeCalculationByFWHM(ProfileMetric):
    """
    This metric calculates the field size of a profile by finding the full width at half maximum (FWHM) of the profile. 
    The FWHM is calculated by finding the indices of the left and right transitions in the profile, where the values cross half of the maximum value. 
    The field size is then calculated by taking the difference between the right and left transition indices and multiplying by the distance per pixel in mm. 
    Where the edges of a region are in between indices, the indices closer to the center are used.
    """
    name = "Field Size Calculation by FWHM"
    unit = "mm"

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        left_index, right_index = get_field_indices(self.profile.values)
        return (right_index - left_index + 1) / self.profile.dpmm

class FlatnessCalculationByVariance(ProfileMetric):
    """
    This metric calculates the flatness of a profile by taking 
    80% of the field region calculated using Full Width Half Max (FWHM) and finding (max-min)/(max+min). 
    This assumes each pixel in the profile corresponds to a consistent length in mm, 
    which may not always be the case.
    Where the edges of a region are in between indices, the indices closer to the center are used. 
    """
    name = "Flatness Calculation by Variance"
    unit = "%"

    def __init__(self, in_field_ratio: float = 0.8, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)
        self.in_field_ratio = in_field_ratio

    def calculate(self) -> float:
        values = self.profile.values
        cax_index = self.profile.cax_index
        left_field_index, right_field_index = get_field_indices(values)
        if left_field_index > cax_index or right_field_index < cax_index:
            raise ValueError("CAX index is not between the left and right field indices.")

        left_roi_index = math.ceil(cax_index - (cax_index - left_field_index) * self.in_field_ratio) # Round towards center
        right_roi_index = math.floor(cax_index + (right_field_index - cax_index) * self.in_field_ratio) # Round towards center

        return (
            100
            * (values[left_roi_index:right_roi_index+1].max() - values[left_roi_index:right_roi_index+1].min())
            / (values[left_roi_index:right_roi_index+1].max() + values[left_roi_index:right_roi_index+1].min())
        )

class FlatnessCalculationByRatio(ProfileMetric):
    """
    This metric calculates the flatness ratio of a profile based on the IEC Standard 976. 
    The region of interest (ROI) is dependent on the field size, which is determined by FWHM. 
    The ratio is then the max/min within the ROI. 
    Where the edges of a region are in between indices, the indices closer to the center are used.
    """
    name = "Flatness Calculation by Ratio (IEC)"
    unit = "%"

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        
        values = self.profile.values
        cax_index = self.profile.cax_index
        left_field_index, right_field_index = get_field_indices(values)
        if left_field_index > cax_index or right_field_index < cax_index:
            raise ValueError("CAX index is not between the left and right field indices.")

        left_length_mm = (cax_index - left_field_index) / self.profile.dpmm
        right_length_mm = (right_field_index - cax_index) / self.profile.dpmm

        if left_length_mm < 100:
            left_roi_index = math.ceil(cax_index - (left_length_mm - 20) * self.profile.dpmm)  # Round towards center
        elif left_length_mm < 300:
            left_roi_index = math.ceil(cax_index - (left_length_mm * 0.8) * self.profile.dpmm)
        else:
            left_roi_index = math.ceil(cax_index - (left_length_mm - 60) * self.profile.dpmm)

        if right_length_mm < 100:
            right_roi_index = math.floor(cax_index + (right_length_mm - 20) * self.profile.dpmm)  # Round towards center
        elif right_length_mm < 300:
            right_roi_index = math.floor(cax_index + (right_length_mm * 0.8) * self.profile.dpmm)
        else:
            right_roi_index = math.floor(cax_index + (right_length_mm - 60) * self.profile.dpmm)
        return (
            100
            * (values[left_roi_index:right_roi_index+1].max())
            / (values[left_roi_index:right_roi_index+1].min())
        )

class FlatnessCalculationByCaxVariance(ProfileMetric):
    """
    This metric calculates the flatness of a profile by finding 
    (max-min)/CAX value within the field found by FWHM. 
    Where the edges of a region are in between indices, the indices closer to the center are used.
    """
    name = "Flatness Calculation by CAX Variance"
    unit = ""

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        
        values = self.profile.values
        cax_value = get_cax_value(values)
        cax_index = self.profile.cax_index
        left_field_index, right_field_index = get_field_indices(values)
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
    """
    This metric calculates the flatness of a profile by finding 
    max/CAX value within 90% of the field found by FWHM. 
    Where the edges of a region are in between indices, the indices closer to the center are used.
    """
    name = "Flatness Calculation by CAX Ratio"
    unit = ""

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        values = self.profile.values
        cax_value = get_cax_value(values)
        cax_index = self.profile.cax_index
        left_field_index, right_field_index = get_field_indices(values, )
        if left_field_index > cax_index or right_field_index < cax_index:
            raise ValueError("CAX index is not between the left and right field indices.")

        left_roi_index = math.ceil(cax_index - (cax_index - left_field_index) * 0.9)  # Round towards center
        right_roi_index = math.floor(cax_index + (right_field_index - cax_index) * 0.9)  # Round towards center
        return (
            (values[left_roi_index:right_roi_index+1].max())
            / cax_value
        )
    
class SymmetryCalculationByCAXPointDifference(ProfileMetric):
    """
    This metric calculates the symmetry of a profile by finding 
    the maximum difference between symmetric points with respect to the CAX. 
    Where the edges of a region are in between indices, the indices closer to the center are used.
    """
    name = "Symmetry Calculation by CAX Point Difference"
    unit = "%"

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        values = self.profile.values
        cax_value = get_cax_value(values)
        cax_index = self.profile.cax_index
        left_field_index, right_field_index = get_field_indices(values)
        if left_field_index > cax_index or right_field_index < cax_index:
            raise ValueError("CAX index is not between the left and right field indices.")

        left_roi_index = math.ceil(cax_index - (cax_index - left_field_index) * 0.8)  # Round towards center
        right_roi_index = math.floor(cax_index + (right_field_index - cax_index) * 0.8)  # Round towards center

        left_index = math.floor(cax_index)
        right_index = math.ceil(cax_index)

        max_difference = 0
        while left_index >= left_roi_index and right_index <= right_roi_index:
            difference = abs(values[left_index] - values[right_index])
            if difference > max_difference:
                max_difference = difference
            left_index -= 1
            right_index += 1

        return max_difference / cax_value * 100
    
class SymmetryCalculationByPointRatio(ProfileMetric):
    """
    This metric calculates the symmetry point ratio of a profile based on the IEC Standard 976.  
    The field size is determined using FWHM and the ROI from the length of the field. 
    The ratio is calculated by finding the maximum ratio between symmetric points with respect to the beam centre. 
    This assumes each pixel in the profile corresponds to a consistent length in mm, which may not always be the case.
    Where the edges of a region are in between indices, the indices closer to the center are used.
    """
    name = "Symmetry Calculation by Point Ratio (IEC 976)"
    unit = "%"

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        values = self.profile.values
        left_field_index, right_field_index = get_field_indices(values)
        beam_centre_index = (left_field_index + right_field_index) / 2

        left_length_mm = (beam_centre_index - left_field_index) / self.profile.dpmm
        right_length_mm = (right_field_index - beam_centre_index) / self.profile.dpmm

        if left_length_mm < 100:
            left_roi_index = math.ceil(beam_centre_index - (left_length_mm - 20) * self.profile.dpmm)  # Round towards center
        elif left_length_mm < 300:
            left_roi_index = math.ceil(beam_centre_index - (left_length_mm * 0.8) * self.profile.dpmm)
        else:
            left_roi_index = math.ceil(beam_centre_index - (left_length_mm - 60) * self.profile.dpmm)

        if right_length_mm < 100:
            right_roi_index = math.floor(beam_centre_index + (right_length_mm - 20) * self.profile.dpmm)  # Round towards center
        elif right_length_mm < 300:
            right_roi_index = math.floor(beam_centre_index + (right_length_mm * 0.8) * self.profile.dpmm)
        else:
            right_roi_index = math.floor(beam_centre_index + (right_length_mm - 60) * self.profile.dpmm)

        left_index = math.floor(beam_centre_index)
        right_index = math.ceil(beam_centre_index)

        max_difference = 0
        max_right_value = 1
        max_left_value = 1
        while left_index >= left_roi_index and right_index <= right_roi_index:
            difference = values[right_index] - values[left_index]
            if abs(difference) > abs(max_difference):
                max_difference = difference
                max_right_value = values[right_index]
                max_left_value = values[left_index]
            left_index -= 1
            right_index += 1

        if max_difference > 0:
            return max_right_value / max_left_value * 100
        else:
            return max_left_value / max_right_value * 100
        
    
class SymmetryCalculationByLocalPointDifference(ProfileMetric):
    name = "Symmetry Calculation by Local Point Difference"
    unit = ""

    def __init__(self, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)

    def calculate(self) -> float:
        raise NotImplementedError("This metric does not make sense for computer generated EPIDs and is not implemented.")
    
class SymmetryCalculationByArea(ProfileMetric):
    """
    This metric calculates the symmetry of a profile by finding the area under the curve on either side of the CAX within a specified region of interest (ROI) and finding the difference divided by the sum. 
    The area is approximated using trapezoidal integration. 
    Where the edges of a region are in between indices, the indices closer to the center are used.
    """
    name = "Symmetry Calculation by Area"
    unit = ""

    def __init__(self, in_field_ratio: float = 0.8, color="g", linestyle="-."):
        super().__init__(color=color, linestyle=linestyle)
        self.in_field_ratio = in_field_ratio

    def calculate(self) -> float:
        values = self.profile.values
        left_field_index, right_field_index = get_field_indices(values)
        beam_centre_index = (left_field_index + right_field_index) / 2

        left_roi_index = math.ceil(beam_centre_index - (beam_centre_index - left_field_index) * self.in_field_ratio)  # Round towards center
        right_roi_index = math.floor(beam_centre_index + (right_field_index - beam_centre_index) * self.in_field_ratio)  # Round towards center

        left_index = math.floor(beam_centre_index)
        right_index = math.ceil(beam_centre_index)

        left_area_sum = 0
        right_area_sum = 0
        while left_index >= left_roi_index and right_index <= right_roi_index :
            left_area_sum += values[left_index] + (values[left_index - 1] - values[left_index]) / 2 
            right_area_sum += values[right_index] + (values[right_index + 1] - values[right_index]) / 2
            left_index -= 1
            right_index += 1
        return (right_area_sum - left_area_sum) / (right_area_sum + left_area_sum) * 200

def run_analysis_on_path(dcm_path) -> str:
    try:
        analysis = FieldProfileAnalysis(str(dcm_path))
        analysis.analyze(
            centering=Centering.BEAM_CENTER,
            #centering=Centering.GEOMETRIC_CENTER,
            normalization=Normalization.NONE,
            edge_type=Edge.FWHM,
            ground=True,
            metrics=(
                SymmetryPointDifferenceMetric(), 

                FieldsizeCalculationByFWHM(),
                FlatnessCalculationByVariance(),
                FlatnessCalculationByRatio(), 
                FlatnessCalculationByCaxVariance(),
                FlatnessCalculationByCaxRatio(), 
                
                SymmetryCalculationByCAXPointDifference(),
                SymmetryCalculationByPointRatio(),
                SymmetryCalculationByArea(),
            ),
        )
        return analysis.results()
    except Exception as e:
        return f"Error analyzing {dcm_path.name}: {str(e)}"


## TESTING DELETE LATER
#path = 'Solstice-m12_d18_2025-FS_EPID_MLC 10x38.dcm'
path = 'Solstice-m12_d18_2025-FS_EPID_Jaw 10x10.dcm'
#path = 'Test/perfect_blur_10x10.dcm'
# field_analyzer = FieldProfileAnalysis(path)
# field_analyzer.analyze(
#     centering=Centering.BEAM_CENTER,
#     # x_width=0.02,
#     # y_width=0.02,
#     normalization=Normalization.BEAM_CENTER,
#     edge_type=Edge.FWHM,
#     ground=True,
#     metrics=(
#         PenumbraLeftMetric(),
#         PenumbraRightMetric(),
#         SymmetryAreaMetric(),
#         FlatnessDifferenceMetric(),
#         SymmetryPointDifferenceMetric(),
#         FlatnessCalculationByVariance(),
#         FlatnessRatioMetric(),
#         FlatnessCalculationByRatio(), 
#         FlatnessCalculationByCaxVariance(),
#         FlatnessCalculationByCaxRatio(),
#         SymmetryCalculationByCAXPointDifference(),
#         SymmetryCalculationByPointRatio(),
#         SymmetryCalculationByArea()
#     ),
# )
# print(field_analyzer.results())
print(run_analysis_on_path(path))