import pytest

NOT_IMPLEMENTED = pytest.mark.skip(reason="not yet implemented")


@NOT_IMPLEMENTED
def test_analyze_all_mirrors_folder_structure(tmp_path):
    """analyze_all should write one result per DICOM under Analysis/, mirroring the subfolders under Images/."""


@NOT_IMPLEMENTED
def test_analyze_all_output_formats(tmp_path):
    """output_format='json' should write valid JSON files; the default should write pformat text with a .txt suffix."""


@NOT_IMPLEMENTED
def test_analyze_all_reports_failures(tmp_path):
    """A DICOM that fails to analyze should be counted in the final 'done with N error(s)' status and get a result file containing the error."""


@NOT_IMPLEMENTED
def test_analyze_all_with_no_dicoms(tmp_path):
    """analyze_all should report that no .dcm files were found and write nothing when Images/ is empty."""


@NOT_IMPLEMENTED
def test_run_analysis_respects_options(tmp_path):
    """analysis_gui.run_analysis should only generate the selected image types and only analyze when 'Run analysis on generated images' is selected."""


@NOT_IMPLEMENTED
def test_run_analysis_stages_resources(tmp_path):
    """run_analysis should copy each selected image type's resources into its image folder."""


@NOT_IMPLEMENTED
def test_gui_shows_error_status_on_failure():
    """When run_analysis raises, the GUI status bar should show the exception message (regression test for the unbound-exception lambda)."""
