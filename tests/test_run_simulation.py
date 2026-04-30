import pytest

from rise.application.use_cases.run_simulation import RunSimulation
from rise.application.dtos.simulation_result import SimulationResult


def test_run_simulation_returns_expected_result(valid_engine) -> None:
    use_case = RunSimulation()

    result = use_case.execute(valid_engine)

    assert isinstance(result, SimulationResult)
    assert result.engine_name == "pressure-fed-test"
    assert result.expansion_ratio == pytest.approx(6.0)
    assert result.thrust_n == pytest.approx(3905.64)
    assert result.specific_impulse_s == pytest.approx(221.258, abs=1e-3)