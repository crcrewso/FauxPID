from pylinac.core.image_generator import AS1200Image
import pylinac.core.image_generator.layers as layers
from linacdicomimagesuite.metrics import run_analysis_on_path

def test_perfect_image():
    simulator_instance = AS1200Image()
    simulator_instance.add_layer(
        layers.PerfectFieldLayer(field_size_mm=(100, 100))
    )
    file_out_name = "test_perfect_image.dcm"

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