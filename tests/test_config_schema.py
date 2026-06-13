import tempfile
from pathlib import Path

import pytest
import yaml

from rise.application.dtos.simulation_input import SimulationInput
from rise.infrastructure.config.engine_config_loader import load_engine_config
from rise.infrastructure.config.schema import EngineConfigSchema


@pytest.fixture
def valid_config() -> dict:
    return {
        "name": "test-engine",
        "throat_area_m2": 0.0008,
        "exit_area_m2": 0.0048,
        "chamber_pressure_pa": 2_000_000.0,
        "ambient_pressure_pa": 101_325.0,
        "mass_flow_kg_s": 1.8,
        "characteristic_length_m": 0.762,
        "contraction_ratio": 5.0,
        "convergent_half_angle_deg": 30.0,
        "divergent_half_angle_deg": 15.0,
        "nozzle_length_method": "80_percent_bell",
        "oxidizer": "LOX",
        "fuel": "LH2",
        "mixture_ratio": 4.0,
        "initial_chamber_pressure_pa": 2_000_000.0,
        "burn_time_s": 10.0,
        "time_step_s": 0.0005,
        "propellant_mass_kg": 18.0,
        "min_chamber_pressure_pa": 500_000.0,
        "mass_flow_decay_model": "constant",
    }


def test_schema_validates_required_fields(valid_config: dict) -> None:
    schema = EngineConfigSchema(**valid_config)
    assert schema.name == "test-engine"
    assert schema.throat_area_m2 == 0.0008
    assert schema.exit_area_m2 == 0.0048


def test_schema_allows_minimal_config() -> None:
    """Only required fields should be enough to create a schema."""
    minimal = {
        "name": "minimal",
        "throat_area_m2": 0.0008,
        "exit_area_m2": 0.0048,
        "chamber_pressure_pa": 2_000_000.0,
        "ambient_pressure_pa": 101_325.0,
        "mass_flow_kg_s": 1.8,
        "characteristic_length_m": 0.762,
        "contraction_ratio": 5.0,
        "convergent_half_angle_deg": 30.0,
        "divergent_half_angle_deg": 15.0,
        "nozzle_length_method": "80_percent_bell",
    }
    schema = EngineConfigSchema(**minimal)
    assert schema.oxidizer is None
    assert schema.fuel is None
    assert schema.burn_time_s is None


def test_schema_rejects_exit_area_smaller_than_throat() -> None:
    """Cross-field validation: exit_area must be >= throat_area."""
    bad = {
        "name": "bad",
        "throat_area_m2": 0.0048,
        "exit_area_m2": 0.0008,
        "chamber_pressure_pa": 2_000_000.0,
        "ambient_pressure_pa": 101_325.0,
        "mass_flow_kg_s": 1.8,
        "characteristic_length_m": 0.762,
        "contraction_ratio": 5.0,
        "convergent_half_angle_deg": 30.0,
        "divergent_half_angle_deg": 15.0,
        "nozzle_length_method": "80_percent_bell",
    }
    with pytest.raises(ValueError, match="exit_area_m2 must be >= throat_area_m2"):
        EngineConfigSchema(**bad)


def test_schema_rejects_negative_pressure() -> None:
    """Negative chamber pressure should be rejected by Pydantic."""
    bad = {
        "name": "bad",
        "throat_area_m2": 0.0008,
        "exit_area_m2": 0.0048,
        "chamber_pressure_pa": -1.0,
        "ambient_pressure_pa": 101_325.0,
        "mass_flow_kg_s": 1.8,
        "characteristic_length_m": 0.762,
        "contraction_ratio": 5.0,
        "convergent_half_angle_deg": 30.0,
        "divergent_half_angle_deg": 15.0,
        "nozzle_length_method": "80_percent_bell",
    }
    with pytest.raises(ValueError):
        EngineConfigSchema(**bad)


def test_schema_rejects_missing_required_field() -> None:
    """Missing required field should raise a validation error."""
    incomplete = {
        "name": "incomplete",
        "throat_area_m2": 0.0008,
    }
    with pytest.raises(ValueError):
        EngineConfigSchema(**incomplete)


def test_loader_raises_clean_error_on_bad_yaml() -> None:
    """load_engine_config should raise a clean ValueError with details."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "bad.yaml"
        path.write_text(
            yaml.dump(
                {
                    "name": "bad",
                    "throat_area_m2": 0.0008,
                    "exit_area_m2": 0.0004,
                    "chamber_pressure_pa": -1.0,
                    "ambient_pressure_pa": 101_325.0,
                    "mass_flow_kg_s": 1.8,
                    "characteristic_length_m": 0.762,
                    "contraction_ratio": 5.0,
                    "convergent_half_angle_deg": 30.0,
                    "divergent_half_angle_deg": 15.0,
                    "nozzle_length_method": "80_percent_bell",
                }
            )
        )

        with pytest.raises(ValueError, match="Invalid engine config"):
            load_engine_config(path)


def test_loader_returns_simulation_input(valid_config: dict) -> None:
    """A valid YAML should produce a SimulationInput DTO."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "engine.yaml"
        path.write_text(yaml.dump(valid_config))

        result = load_engine_config(path)
        assert isinstance(result, SimulationInput)
        assert result.engine_name == "test-engine"
        assert result.throat_area_m2 == 0.0008
        assert result.exit_area_m2 == 0.0048
        assert result.oxidizer == "LOX"
        assert result.fuel == "LH2"


def test_loader_parses_real_config_file() -> None:
    """The real pressure_fed_test.yaml should load without errors."""
    path = Path("configs/engines/pressure_fed_test.yaml")
    result = load_engine_config(path)
    assert isinstance(result, SimulationInput)
    assert result.engine_name == "pressure-fed-test"
    assert result.oxidizer == "LOX"
    assert result.fuel == "LH2"
