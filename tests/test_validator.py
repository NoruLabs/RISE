import json
import tempfile
from pathlib import Path

import pytest

from rise.application.validation.validator import (
    ValidationResult,
    ValidationSummary,
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
    validator = Validator(reference_case_path)

    # Create exact match properties
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
    # Only 5 of the 7 expected values are in ChamberProperties
    # (exit_mach and exit_pressure_pa are from get_performance_at_exit)
    assert len(summary.results) == 5

    for r in summary.results:
        assert r.passed is True
        assert r.percent_error == pytest.approx(0.0)


def test_validator_fails_on_large_error(reference_case_path: Path) -> None:
    validator = Validator(reference_case_path)

    # Create properties with 50% error in gamma
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


def test_validator_validates_transient_initial_pressure(reference_case_path: Path) -> None:
    validator = Validator(reference_case_path)
    expected_pc = validator._reference["operating_conditions"]["chamber_pressure_pa"]

    summary = validator.validate_transient(
        initial_pressure_pa=expected_pc,
        final_pressure_pa=expected_pc * 2.0,
        initial_thrust_n=2000.0,
        final_thrust_n=4000.0,
        initial_isp_s=350.0,
        final_isp_s=380.0,
    )

    assert summary.all_passed is True
    assert summary.results[0].metric == "initial_chamber_pressure_pa"
    assert summary.results[0].percent_error == pytest.approx(0.0, abs=0.01)


def test_validator_fails_transient_with_wrong_pressure(reference_case_path: Path) -> None:
    validator = Validator(reference_case_path)
    expected_pc = validator._reference["operating_conditions"]["chamber_pressure_pa"]

    summary = validator.validate_transient(
        initial_pressure_pa=expected_pc * 1.5,  # 50% error
        final_pressure_pa=expected_pc * 2.0,
        initial_thrust_n=2000.0,
        final_thrust_n=4000.0,
        initial_isp_s=350.0,
        final_isp_s=380.0,
    )

    assert summary.all_passed is False
    assert summary.results[0].percent_error == pytest.approx(50.0, abs=0.1)
