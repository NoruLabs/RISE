import json
import tempfile
from pathlib import Path

import pytest

from rise.application.validation.validator import (
    Validator,
)
from rise.infrastructure.cea.rocketcea_adapter import ChamberProperties


@pytest.fixture
def reference_case_path() -> Path:
    return Path("research/reference_cases/lox_lh2_2mpa_mr4_eps6.json")


def test_validator_loads_reference_case(reference_case_path: Path) -> None:
    validator = Validator(reference_case_path)
    assert validator._reference["name"] == "LOX_LH2_2MPa_MR4_eps6"
    assert validator._reference["propellants"]["oxidizer"] == "LOX"
    assert validator._reference["propellants"]["fuel"] == "LH2"


def test_validator_passes_on_exact_match(reference_case_path: Path) -> None:
    """Steady-state validation with exact match should pass."""
    validator = Validator(reference_case_path)

    expected = validator._reference["expected_values"]
    props = ChamberProperties(
        gamma=expected["gamma"],
        molecular_weight_kg_per_kmol=expected["molecular_weight_kg_per_kmol"],
        chamber_temperature_k=expected["chamber_temperature_k"],
        cstar_m_s=expected["cstar_m_s"],
        isp_vac_s=expected["isp_vac_s"],
        isp_sea_level_s=387.25,
    )

    summary = validator.validate(props)
    assert summary.all_passed is True
    assert len(summary.results) == 5

    for r in summary.results:
        assert r.passed is True
        assert r.percent_error == pytest.approx(0.0)
        assert r.absolute_error == pytest.approx(0.0)


def test_validator_fails_on_large_error(reference_case_path: Path) -> None:
    """Steady-state validation with 50% error should fail."""
    validator = Validator(reference_case_path)

    expected = validator._reference["expected_values"]
    props = ChamberProperties(
        gamma=expected["gamma"] * 1.5,
        molecular_weight_kg_per_kmol=expected["molecular_weight_kg_per_kmol"],
        chamber_temperature_k=expected["chamber_temperature_k"],
        cstar_m_s=expected["cstar_m_s"],
        isp_vac_s=expected["isp_vac_s"],
        isp_sea_level_s=387.25,
    )

    summary = validator.validate(props)
    assert summary.all_passed is False

    gamma_result = [r for r in summary.results if r.metric == "gamma"][0]
    assert gamma_result.passed is False
    assert gamma_result.percent_error == pytest.approx(50.0, abs=0.1)
    assert gamma_result.absolute_error == pytest.approx(0.588, abs=0.001)


def test_validator_validates_steady_state_performance(reference_case_path: Path) -> None:
    """Steady-state validation should check thrust, Isp, and pressure."""
    validator = Validator(reference_case_path)
    expected = validator._reference["expected_values"]

    # Use known CEA values for thrust and Isp
    summary = validator.validate_steady_state(
        thrust_n=6937.82,
        specific_impulse_s=393.034,
        chamber_pressure_pa=expected["exit_pressure_pa"],
    )

    # Thrust and Isp should be within 5% tolerance
    thrust_result = [r for r in summary.results if r.metric == "thrust_n"]
    if thrust_result:
        assert thrust_result[0].passed is True

    isp_result = [r for r in summary.results if r.metric == "specific_impulse_s"]
    if isp_result:
        assert isp_result[0].passed is True


def test_validator_validates_transient_initial_conditions(reference_case_path: Path) -> None:
    """Transient validation should check initial conditions."""
    validator = Validator(reference_case_path)
    expected_pc = validator._reference["operating_conditions"]["chamber_pressure_pa"]

    summary = validator.validate_transient(
        time_s=[0.0, 1.0, 2.0],
        actual_pressure_pa=[expected_pc, expected_pc * 1.1, expected_pc * 1.2],
    )

    assert summary.all_passed is True
    assert summary.results[0].metric == "initial_chamber_pressure_pa"
    assert summary.results[0].rms_error == pytest.approx(0.0, abs=0.01)


def test_validator_fails_transient_with_wrong_initial_pressure(reference_case_path: Path) -> None:
    """Transient validation should fail when initial pressure is wrong."""
    validator = Validator(reference_case_path)
    expected_pc = validator._reference["operating_conditions"]["chamber_pressure_pa"]

    summary = validator.validate_transient(
        time_s=[0.0, 1.0, 2.0],
        actual_pressure_pa=[expected_pc * 1.5, expected_pc * 1.1, expected_pc * 1.2],
    )

    assert summary.all_passed is False
    assert summary.results[0].rms_error == pytest.approx(50.0, abs=0.1)


def test_validator_computes_rms_error(reference_case_path: Path) -> None:
    """Transient validation should compute RMS error when reference data is provided."""
    validator = Validator(reference_case_path)

    reference_pressure = [2_000_000.0, 2_500_000.0, 3_000_000.0]
    actual_pressure = [2_000_000.0, 2_550_000.0, 3_100_000.0]

    summary = validator.validate_transient(
        time_s=[0.0, 1.0, 2.0],
        reference_pressure_pa=reference_pressure,
        actual_pressure_pa=actual_pressure,
    )

    # Find the RMS result
    rms_result = [r for r in summary.results if "rms" in r.metric]
    assert len(rms_result) > 0
    assert rms_result[0].rms_error > 0.0
    assert rms_result[0].max_error > 0.0
    assert rms_result[0].mean_error > 0.0


def test_validator_generates_markdown_report(reference_case_path: Path) -> None:
    """Validator should generate a markdown report with tables."""
    validator = Validator(reference_case_path)
    expected = validator._reference["expected_values"]

    props = ChamberProperties(
        gamma=expected["gamma"],
        molecular_weight_kg_per_kmol=expected["molecular_weight_kg_per_kmol"],
        chamber_temperature_k=expected["chamber_temperature_k"],
        cstar_m_s=expected["cstar_m_s"],
        isp_vac_s=expected["isp_vac_s"],
        isp_sea_level_s=387.25,
    )

    steady_summary = validator.validate(props)
    transient_summary = validator.validate_transient(
        time_s=[0.0],
        actual_pressure_pa=[validator._reference["operating_conditions"]["chamber_pressure_pa"]],
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = Path(tmpdir) / "validation_report.md"
        validator.generate_report(steady_summary, transient_summary, report_path)

        assert report_path.exists()
        content = report_path.read_text()
        assert "# Validation Report" in content
        assert "Steady-State Validation" in content
        assert "Transient Validation" in content
        assert "PASS" in content
        assert "Final Verdict" in content


def test_validator_print_summary_format(reference_case_path: Path) -> None:
    validator = Validator(reference_case_path)
    expected = validator._reference["expected_values"]
    props = ChamberProperties(
        gamma=expected["gamma"],
        molecular_weight_kg_per_kmol=expected["molecular_weight_kg_per_kmol"],
        chamber_temperature_k=expected["chamber_temperature_k"],
        cstar_m_s=expected["cstar_m_s"],
        isp_vac_s=expected["isp_vac_s"],
        isp_sea_level_s=387.25,
    )

    summary = validator.validate(props)
    text = validator.print_summary(summary)
    assert "Validation: LOX_LH2_2MPa_MR4_eps6" in text
    assert "PASS" in text
    assert "Overall: PASS" in text


def test_validator_expected_error_metrics(reference_case_path: Path) -> None:
    """Test with known error values to verify error metric correctness.

    Uses a 10% offset from reference to verify absolute and percent
    error calculations are deterministic.
    """
    validator = Validator(reference_case_path)
    expected = validator._reference["expected_values"]

    # Create properties with exactly 10% error
    props = ChamberProperties(
        gamma=expected["gamma"] * 1.1,
        molecular_weight_kg_per_kmol=expected["molecular_weight_kg_per_kmol"] * 1.1,
        chamber_temperature_k=expected["chamber_temperature_k"] * 1.1,
        cstar_m_s=expected["cstar_m_s"] * 1.1,
        isp_vac_s=expected["isp_vac_s"] * 1.1,
        isp_sea_level_s=387.25,
    )

    summary = validator.validate(props)

    # All results should have exactly 10% error
    for r in summary.results:
        assert r.percent_error == pytest.approx(10.0, abs=0.01)
        assert r.passed is False  # 10% > 5% tolerance

    assert summary.all_passed is False


def test_validator_rms_error_computation() -> None:
    """RMS error computation should be mathematically correct."""
    validator = Validator.__new__(Validator)

    reference = [1.0, 2.0, 3.0]
    actual = [1.1, 2.2, 3.3]

    rms = validator._rms_error(reference, actual)
    # RMS of 10% errors = 10.0%
    assert rms == pytest.approx(10.0, abs=0.01)

    mean = validator._mean_error(reference, actual)
    assert mean == pytest.approx(10.0, abs=0.01)

    max_err = validator._max_error(reference, actual)
    assert max_err == pytest.approx(10.0, abs=0.01)


def test_validator_rms_error_returns_zero_when_all_reference_zero() -> None:
    """RMS error should return 0.0 when all reference values are zero."""
    validator = Validator.__new__(Validator)

    rms = validator._rms_error([0.0, 0.0, 0.0], [1.0, 2.0, 3.0])
    assert rms == 0.0


def test_validator_steady_state_fails_on_large_error() -> None:
    """Steady-state validation should fail when metrics exceed tolerance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ref_path = Path(tmpdir) / "ref.json"
        ref_path.write_text(
            json.dumps(
                {
                    "name": "Test",
                    "expected_values": {
                        "thrust_n": 1000.0,
                        "specific_impulse_s": 200.0,
                        "chamber_pressure_pa": 2_000_000.0,
                    },
                    "tolerance": {
                        "thrust_n": 5.0,
                        "specific_impulse_s": 5.0,
                        "chamber_pressure_pa": 5.0,
                    },
                }
            )
        )
        validator = Validator(ref_path)
        summary = validator.validate_steady_state(
            thrust_n=1000.0 * 1.2,
            specific_impulse_s=200.0 * 1.2,
            chamber_pressure_pa=2_000_000.0 * 1.2,
        )

        assert summary.all_passed is False
        for r in summary.results:
            assert r.passed is False
            assert r.percent_error == pytest.approx(20.0, abs=0.1)


def test_validator_transient_fails_on_large_pressure_error(
    reference_case_path: Path,
) -> None:
    """Transient validation should fail when pressure curve has large errors."""
    validator = Validator(reference_case_path)
    expected_pc = validator._reference["operating_conditions"]["chamber_pressure_pa"]

    summary = validator.validate_transient(
        time_s=[0.0, 1.0, 2.0],
        reference_pressure_pa=[expected_pc, expected_pc, expected_pc],
        actual_pressure_pa=[expected_pc * 1.5, expected_pc * 1.5, expected_pc * 1.5],
    )

    assert summary.all_passed is False
    rms_result = [r for r in summary.results if "rms" in r.metric]
    assert len(rms_result) > 0
    assert rms_result[0].passed is False


def test_validator_transient_fails_on_large_thrust_error(
    reference_case_path: Path,
) -> None:
    """Transient validation should fail when thrust curve has large errors."""
    validator = Validator(reference_case_path)
    expected_thrust = 1000.0

    summary = validator.validate_transient(
        time_s=[0.0, 1.0, 2.0],
        reference_thrust_n=[expected_thrust, expected_thrust, expected_thrust],
        actual_thrust_n=[expected_thrust * 2.0, expected_thrust * 2.0, expected_thrust * 2.0],
    )

    assert summary.all_passed is False
    rms_result = [r for r in summary.results if "rms" in r.metric]
    assert len(rms_result) > 0
    assert rms_result[0].passed is False
