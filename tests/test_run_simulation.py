import pytest

from rise.application.dtos.simulation_input import SimulationInput
from rise.application.dtos.simulation_result import SimulationResult
from rise.application.use_cases.run_simulation import RunSimulation


def test_run_simulation_returns_expected_result() -> None:
    request = SimulationInput(
        engine_name="pressure-fed-test",
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=1.8,
        exit_velocity_m_s=2_200.0,
        exit_pressure_pa=90_000.0,
    )

    use_case = RunSimulation()
    result = use_case.execute(request)

    assert isinstance(result, SimulationResult)
    assert result.engine_name == "pressure-fed-test"
    assert result.expansion_ratio == pytest.approx(6.0)
    assert result.thrust_n == pytest.approx(3905.64)
    assert result.specific_impulse_s == pytest.approx(221.258, abs=1e-3)