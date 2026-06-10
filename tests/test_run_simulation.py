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
        oxidizer="LOX",
        fuel="LH2",
        gamma=1.22,
        molecular_weight_kg_per_kmol=22.0,
        chamber_temperature_k=3483.35,
        characteristic_length_m=0.762,
        contraction_ratio=5.0,
        convergent_half_angle_deg=30.0,
        divergent_half_angle_deg=15.0,
        nozzle_length_method="80_percent_bell",
        initial_chamber_pressure_pa=2_000_000.0,
        burn_time_s=10.0,
        time_step_s=0.01,
        propellant_mass_kg=18.0,
        mass_flow_decay_model="constant",
    )

    use_case = RunSimulation()
    result = use_case.execute(request)

    assert isinstance(result, SimulationResult)
    assert result.engine_name == "pressure-fed-test"
    assert result.expansion_ratio == pytest.approx(6.0)
    assert result.thrust_n == pytest.approx(3905.64)
    assert result.specific_impulse_s == pytest.approx(221.258, abs=1e-3)

    assert result.geometry.throat_diameter_m == pytest.approx(0.0319154, abs=1e-6)
    assert result.geometry.throat_radius_m == pytest.approx(0.0159577, abs=1e-6)
    assert result.geometry.exit_diameter_m == pytest.approx(0.0781764, abs=1e-6)
    assert result.geometry.chamber_diameter_m == pytest.approx(0.0713650, abs=1e-6)
    assert result.geometry.chamber_volume_m3 == pytest.approx(0.0006096, abs=1e-6)
    assert result.geometry.chamber_length_m == pytest.approx(0.1524, abs=1e-6)
    assert result.geometry.converging_length_m == pytest.approx(0.0341643, abs=1e-6)
    assert result.geometry.diverging_length_m == pytest.approx(0.0863242, abs=1e-6)
    assert result.geometry.expansion_ratio == pytest.approx(6.0)

    assert result.transient is not None
    assert len(result.transient.time_s) > 0
    assert result.transient.chamber_pressure_pa[0] == pytest.approx(2_000_000.0)
    assert result.transient.chamber_pressure_pa[-1] == pytest.approx(3_950_000.0, rel=0.02)
    assert result.transient.thrust_n[-1] > result.transient.thrust_n[0]