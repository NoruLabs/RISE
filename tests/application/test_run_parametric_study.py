"""Unit tests for RunParametricStudy use case."""
import pytest

from rise.application.dtos.simulation_input import SimulationInput
from rise.application.use_cases.run_parametric_study import RunParametricStudy

# Minimal engine config that does NOT require RocketCEA (manual thermo)
_BASE = SimulationInput(
    engine_name="test-engine",
    throat_area_m2=0.0008,
    exit_area_m2=0.0048,
    chamber_pressure_pa=5_000_000,
    ambient_pressure_pa=101_325,
    mass_flow_kg_s=1.8,
    characteristic_length_m=1.143,
    contraction_ratio=5.0,
    convergent_half_angle_deg=30.0,
    divergent_half_angle_deg=15.0,
    nozzle_length_method="conical",
    gamma=1.2,
    molecular_weight_kg_per_kmol=20.0,
    chamber_temperature_k=3000.0,
    exit_velocity_m_s=3500.0,
    exit_pressure_pa=50_000.0,
)


def test_parametric_returns_one_result_per_value():
    uc = RunParametricStudy()
    result = uc.execute(_BASE, "mass_flow_kg_s", [1.0, 1.5, 2.0])
    assert len(result.results) == 3
    assert result.values == [1.0, 1.5, 2.0]
    assert result.parameter == "mass_flow_kg_s"


def test_parametric_thrust_differs_across_values():
    uc = RunParametricStudy()
    result = uc.execute(_BASE, "mass_flow_kg_s", [1.0, 2.0, 3.0])
    thrusts = [r.thrust_n for r in result.results]
    assert len({round(t, 2) for t in thrusts}) == 3


def test_parametric_raises_on_too_many_values():
    uc = RunParametricStudy()
    with pytest.raises(ValueError, match="50 values"):
        uc.execute(_BASE, "mass_flow_kg_s", list(range(51)))


def test_parametric_raises_on_invalid_parameter():
    uc = RunParametricStudy()
    with pytest.raises(ValueError, match="not a valid"):
        uc.execute(_BASE, "nonexistent_field", [1.0])
