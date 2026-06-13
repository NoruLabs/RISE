import pytest

from rise.application.dtos.simulation_result import SimulationResult
from rise.application.dtos.transient_simulation_result import (
    TransientSimulationResult,
)
from rise.domain.services.geometry_service import GeometryResult
from rise.interfaces.presenters.console_presenter import ConsolePresenter


@pytest.fixture
def sample_geometry() -> GeometryResult:
    return GeometryResult(
        throat_diameter_m=0.032,
        throat_radius_m=0.016,
        chamber_volume_m3=0.00061,
        chamber_diameter_m=0.071,
        chamber_length_m=0.152,
        converging_length_m=0.034,
        diverging_length_m=0.086,
        exit_diameter_m=0.078,
        expansion_ratio=6.0,
    )


@pytest.fixture
def sample_result(sample_geometry: GeometryResult) -> SimulationResult:
    return SimulationResult(
        engine_name="test-engine",
        expansion_ratio=6.0,
        thrust_n=1000.0,
        specific_impulse_s=200.0,
        geometry=sample_geometry,
    )


def test_console_presenter_shows_steady_state_output(
    sample_result: SimulationResult,
) -> None:
    presenter = ConsolePresenter()
    output = presenter.present(sample_result)

    assert "RISE" in output
    assert "test-engine" in output
    assert "1000.000" in output
    assert "200.000" in output


def test_console_presenter_shows_transient_burn_complete(
    sample_geometry: GeometryResult,
) -> None:
    transient = TransientSimulationResult(
        time_s=[0.0, 1.0, 2.0],
        chamber_pressure_pa=[2_000_000.0, 2_500_000.0, 3_000_000.0],
        mass_flow_kg_s=[1.0, 1.2, 1.4],
        thrust_n=[1000.0, 1500.0, 2000.0],
        specific_impulse_s=[200.0, 210.0, 220.0],
        remaining_propellant_kg=[10.0, 5.0, 0.0],
        burn_time_s=2.0,
    )
    result = SimulationResult(
        engine_name="test-engine",
        expansion_ratio=6.0,
        thrust_n=1000.0,
        specific_impulse_s=200.0,
        geometry=sample_geometry,
        transient=transient,
    )

    presenter = ConsolePresenter()
    output = presenter.present(result)

    assert "Burn complete at" in output
    assert "2.000" in output


def test_console_presenter_shows_remaining_propellant(
    sample_geometry: GeometryResult,
) -> None:
    transient = TransientSimulationResult(
        time_s=[0.0, 1.0, 2.0],
        chamber_pressure_pa=[2_000_000.0, 2_500_000.0, 3_000_000.0],
        mass_flow_kg_s=[1.0, 1.2, 1.4],
        thrust_n=[1000.0, 1500.0, 2000.0],
        specific_impulse_s=[200.0, 210.0, 220.0],
        remaining_propellant_kg=[10.0, 5.0, 1.0],
        burn_time_s=2.0,
    )
    result = SimulationResult(
        engine_name="test-engine",
        expansion_ratio=6.0,
        thrust_n=1000.0,
        specific_impulse_s=200.0,
        geometry=sample_geometry,
        transient=transient,
    )

    presenter = ConsolePresenter()
    output = presenter.present(result)

    assert "Remaining propellant" in output
    assert "1.000" in output
