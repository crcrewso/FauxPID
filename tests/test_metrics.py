from pylinac.core.image_generator import AS1200Image
import pylinac.core.image_generator.layers as layers
import pytest
from FauxPID.algorithms.metrics import run_analysis_on_path

def test_perfect_image(tmp_path):
    simulator_instance = AS1200Image()
    simulator_instance.add_layer(
        layers.PerfectFieldLayer(field_size_mm=(100, 100))
    )
    file_out_name = tmp_path / "test_perfect_image.dcm"

    simulator_instance.generate_dicom(file_out_name=file_out_name)
    results = run_analysis_on_path(file_out_name)

    assert results["x_metrics"]["Flatness Calculation by Variance (%)"] == 0.0
    assert results["x_metrics"]["Flatness Calculation by Ratio (IEC) (%)"] == 100.0
    assert results["x_metrics"]["Flatness Calculation by CAX Variance"] == 0.0
    assert results["x_metrics"]["Flatness Calculation by CAX Ratio"] == 1.0
    assert results["x_metrics"]["Symmetry Calculation by CAX Point Difference (%)"] == 0.0
    assert results["x_metrics"]["Symmetry Calculation by Point Ratio (IEC 976) (%)"] == 100.0
    assert results["x_metrics"]["Symmetry Calculation by Area (%)"] == 0.0
    assert abs(results["x_metrics"]["Field Size Calculation by FWHM (mm)"] - 100.0) < 1e-1
    assert abs(results["x_metrics"]["CAX Offset from Beam Center (mm)"]) < 1e-3

    assert results["y_metrics"]["Flatness Calculation by Variance (%)"] == 0.0
    assert results["y_metrics"]["Flatness Calculation by Ratio (IEC) (%)"] == 100.0
    assert results["y_metrics"]["Flatness Calculation by CAX Variance"] == 0.0
    assert results["y_metrics"]["Flatness Calculation by CAX Ratio"] == 1.0
    assert results["y_metrics"]["Symmetry Calculation by CAX Point Difference (%)"] == 0.0
    assert results["y_metrics"]["Symmetry Calculation by Point Ratio (IEC 976) (%)"] == 100.0
    assert results["y_metrics"]["Symmetry Calculation by Area (%)"] == 0.0
    assert abs(results["y_metrics"]["Field Size Calculation by FWHM (mm)"] - 100.0) < 1e-1
    assert abs(results["y_metrics"]["CAX Offset from Beam Center (mm)"]) < 1e-3

NOT_IMPLEMENTED = pytest.mark.skip(reason="not yet implemented")


# --- Helper functions ---

@NOT_IMPLEMENTED
def test_get_transition_indices_raises_when_threshold_not_crossed():
    """get_transition_indices should raise ValueError for a profile that never exceeds the threshold."""


@NOT_IMPLEMENTED
def test_get_field_indices_uses_whole_profile_max_when_cax_outside_field():
    """For a field offset so far that the CAX is outside it, the 50% level should come from the profile max, not the CAX value."""


@NOT_IMPLEMENTED
def test_get_cax_value_odd_and_even_lengths():
    """get_cax_value should return the middle value for odd-length profiles and the mean of the two middle values for even lengths."""


# --- Known-answer tests: each generated image should measure as designed ---

@NOT_IMPLEMENTED
def test_field_size_realistic_images():
    """field_size_realistic_10x10 and _20x20 should measure about 100 mm and 200 mm by FWHM in both axes."""


@NOT_IMPLEMENTED
def test_field_size_plus_images():
    """field_size_plus_{10,5,1}_mm images should measure 110, 105 and 101 mm along the enlarged axis and 100 mm along the other."""


@NOT_IMPLEMENTED
def test_cax_offset_images():
    """Each image in profiles.CAX_OFFSETS should report a CAX offset of the designed size, on the designed axis, with the documented sign convention."""


@NOT_IMPLEMENTED
def test_flatness_two_percent_images():
    """flatness_two_percent_variance, _IEC_ratio and _CAX_ratio should give about 2% on their matching metric (2.0, 102.0 and 1.02 respectively)."""


@NOT_IMPLEMENTED
def test_symmetry_two_percent_images():
    """symmetry_two_percent_x_{cax_point_difference,point_ratio,area} should give about 2% on their matching metric in x and about 0 in y."""


@NOT_IMPLEMENTED
def test_symmetry_sign_conventions():
    """symmetry_positive_y and symmetry_negative_y should give opposite signs, matching the conventions in the metric docstrings."""


# --- IEC 60976 regions of interest ---

@NOT_IMPLEMENTED
def test_iec_flatness_roi_width_by_field_size():
    """
    FlatnessCalculationByRatio should use the flattened region IEC 60976 defines for each field size band
    (5-10 cm, 10-30 cm, over 30 cm). Check the ROI width for fields on both sides of each threshold,
    e.g. 8, 10, 15, 30 and 35 cm. Confirm the expected widths against the standard first: whether
    the margin (1 cm, 0.1F, 3 cm per side vs 2 cm, 0.2F, 6 cm per side) is still under discussion.
    """


@NOT_IMPLEMENTED
def test_iec_symmetry_roi_width_by_field_size():
    """SymmetryCalculationByPointRatio should use the same IEC 60976 region as the flatness ratio for each field size band."""


# --- Error handling ---

@NOT_IMPLEMENTED
def test_run_analysis_on_path_raises_for_invalid_file(tmp_path):
    """run_analysis_on_path should raise (not return an error dict) when the file is not a readable DICOM image."""


@NOT_IMPLEMENTED
def test_metrics_raise_when_cax_outside_field():
    """Flatness metrics that need the CAX inside the field should raise ValueError when it is not."""


# --- Open question: profile centering (see docs/DEVELOPERS.md) ---

@NOT_IMPLEMENTED
def test_cax_index_matches_array_midpoint_for_offset_fields():
    """
    For the CAX Offset images, compare pylinac's profile.cax_index with the array midpoint used by get_cax_value()
    under Centering.BEAM_CENTER and Centering.NONE, and pin down which centering mode gives the designed offsets.
    """
