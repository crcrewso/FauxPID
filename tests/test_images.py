import pytest

NOT_IMPLEMENTED = pytest.mark.skip(reason="not yet implemented")


@NOT_IMPLEMENTED
def test_each_generator_writes_expected_files(tmp_path):
    """Each ImageGenerator.generate_*_images method should write exactly the expected DICOM file names into its folder."""


@NOT_IMPLEMENTED
def test_include_png_toggle(tmp_path):
    """With include_png=True every DICOM should have a matching PNG; with include_png=False there should be none."""


@NOT_IMPLEMENTED
def test_metadata_written(tmp_path):
    """Generated DICOMs should carry the gantry, collimator and couch angles and jaw positions passed to add_metadata."""


@NOT_IMPLEMENTED
def test_field_size_20x20_jaw_metadata(tmp_path):
    """field_size_realistic_20x20 should record jaw positions of +/-100 mm; the other field size images +/-50 mm."""


@NOT_IMPLEMENTED
def test_artifact_dead_columns_are_zero(tmp_path):
    """artifact_zero_4_columns should have exactly 4 zero-valued columns at dead_detector_field_position_percent across the field."""


@NOT_IMPLEMENTED
def test_artifact_vertical_bar_metadata(tmp_path):
    """artifact_vertical_bar is currently saved without add_metadata; decide whether that is intended and test the chosen behaviour."""


@NOT_IMPLEMENTED
def test_winston_lutz_metadata_matches_file_name(tmp_path):
    """Every Winston-Lutz file named *_{coll,couch,gantry}_NNN should record angle NNN on that axis and 0 on the others."""


@NOT_IMPLEMENTED
def test_winston_lutz_bb_position(tmp_path):
    """The 6 mm BB found in each Winston-Lutz image should sit at the scenario's offset for that angle, regardless of collimator rotation."""


@NOT_IMPLEMENTED
def test_winston_lutz_scenarios_analyze_with_pylinac(tmp_path):
    """Each Winston-Lutz folder should load in pylinac's WinstonLutz analysis and give the expected BB-to-field offsets (about 0 for 'perfect')."""


@NOT_IMPLEMENTED
def test_generation_is_deterministic_without_noise(tmp_path):
    """With RandomNoiseLayer disabled, generating the same images twice should give identical pixel data."""


def test_from_bb_position_reproduces_fixed_position_scenarios():
    """from_bb_position should give the same offsets as the hand-written tables for scenarios with a fixed BB."""
    from FauxPID.images.winston_lutz import SCENARIOS, WinstonLutzScenario

    positions = {"perfect": (0, 0, 0), "1mm_right": (1, 0, 0), "1mm_out": (0, -1, 0)}
    for scenario in SCENARIOS:
        if scenario.folder not in positions:
            continue
        computed = WinstonLutzScenario.from_bb_position(scenario.folder, "", positions[scenario.folder])
        for axis in ("coll", "couch", "gantry"):
            assert getattr(computed, axis) == pytest.approx(getattr(scenario, axis)), (scenario.folder, axis)


def test_sample_scenario_is_documented_and_not_generated():
    """SAMPLE_SCENARIO is a template: 1.5 mm in projects 1.5 mm up the image, and it is not in SCENARIOS."""
    from FauxPID.images.winston_lutz import SAMPLE_SCENARIO, SCENARIOS

    assert SAMPLE_SCENARIO not in SCENARIOS
    assert SAMPLE_SCENARIO.folder == "1.5mm_in"
    assert SAMPLE_SCENARIO.coll[0] == (-1.5, 0.0)
    assert SAMPLE_SCENARIO.gantry[90] == (-1.5, 0.0)
    assert SAMPLE_SCENARIO.couch[90] == (0.0, -1.5)


def test_every_scenario_has_a_description():
    """Every Winston-Lutz scenario should say in plain language what it simulates."""
    from FauxPID.images.winston_lutz import SCENARIOS

    for scenario in SCENARIOS:
        assert scenario.description.strip(), scenario.folder
