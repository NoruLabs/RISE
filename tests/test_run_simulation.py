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
        oxidizer="LOX",
        fuel="LH2",
        mixture_ratio=4.0,
        characteristic_length_m=0.762,
        contraction_ratio=5.0,
        convergent_half_angle_deg=30.0,
        divergent_half_angle_deg=15.0,
        nozzle_length_method="80_percent_bell",
        initial_chamber_pressure_pa=2_000_000.0,
        burn_time_s=10.0,
        time_step_s=0.0005,
        propellant_mass_kg=18.0,
        min_chamber_pressure_pa=500_000.0,
        mass_flow_decay_model="constant",
    )

    use_case = RunSimulation()
    result = use_case.execute(request)

    assert isinstance(result, SimulationResult)
    assert result.engine_name == "pressure-fed-test"
    assert result.expansion_ratio == pytest.approx(6.0)
    assert result.thrust_n == pytest.approx(6937.82, abs=1e-2)
    assert result.specific_impulse_s == pytest.approx(393.034, abs=1e-3)

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
    assert result.transient.chamber_pressure_pa[-1] == pytest.approx(5_436_476.0, rel=0.02)
    assert result.transient.thrust_n[-1] > result.transient.thrust_n[0]


def test_run_simulation_with_lox_lh2_returns_valid_range() -> None:
    """Full pipeline with LOX/LH2 should return sensible values from CEA."""
    request = SimulationInput(
        engine_name="lox-lh2-test",
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=1.8,
        oxidizer="LOX",
        fuel="LH2",
        mixture_ratio=4.0,
        characteristic_length_m=0.762,
        contraction_ratio=5.0,
        convergent_half_angle_deg=30.0,
        divergent_half_angle_deg=15.0,
        nozzle_length_method="80_percent_bell",
        initial_chamber_pressure_pa=2_000_000.0,
        burn_time_s=10.0,
        time_step_s=0.0005,
        propellant_mass_kg=18.0,
        min_chamber_pressure_pa=500_000.0,
        mass_flow_decay_model="constant",
    )

    use_case = RunSimulation()
    result = use_case.execute(request)

    assert isinstance(result, SimulationResult)
    assert result.engine_name == "lox-lh2-test"
    assert result.expansion_ratio == pytest.approx(6.0)

    # Isp for LOX/LH2 should be between 350 and 500 s
    assert 350.0 < result.specific_impulse_s < 500.0

    # Thrust should be between 3000 and 9000 N for this engine size
    assert 3000.0 < result.thrust_n < 9000.0

    # Geometry should be in reasonable ranges
    assert 0.02 < result.geometry.throat_diameter_m < 0.05
    assert 0.05 < result.geometry.chamber_diameter_m < 0.10
    assert 0.10 < result.geometry.chamber_length_m < 0.25
    assert 0.05 < result.geometry.exit_diameter_m < 0.10

    # Transient should show pressure rise
    assert result.transient is not None
    assert result.transient.chamber_pressure_pa[-1] > result.transient.chamber_pressure_pa[0]
    assert result.transient.thrust_n[-1] > result.transient.thrust_n[0]
    assert result.transient.specific_impulse_s[-1] > result.transient.specific_impulse_s[0]

    # Burn should complete
    assert result.transient.remaining_propellant_kg[-1] == pytest.approx(0.0, abs=1e-6)


def test_run_simulation_raises_on_missing_thermochemistry() -> None:
    """Should raise ValueError when no CEA propellants and no manual thermochemistry."""
    request = SimulationInput(
        engine_name="missing-chemistry",
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=1.8,
        characteristic_length_m=0.762,
        contraction_ratio=5.0,
        convergent_half_angle_deg=30.0,
        divergent_half_angle_deg=15.0,
        nozzle_length_method="80_percent_bell",
    )

    with pytest.raises(ValueError, match="Thermochemistry values missing"):
        RunSimulation().execute(request)


def test_run_simulation_raises_on_missing_exit_conditions() -> None:
    """Should raise ValueError when exit velocity and pressure are missing."""
    request = SimulationInput(
        engine_name="missing-exit",
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=1.8,
        gamma=1.22,
        molecular_weight_kg_per_kmol=22.0,
        chamber_temperature_k=3483.35,
        characteristic_length_m=0.762,
        contraction_ratio=5.0,
        convergent_half_angle_deg=30.0,
        divergent_half_angle_deg=15.0,
        nozzle_length_method="80_percent_bell",
    )

    with pytest.raises(ValueError, match="Exit velocity or exit pressure missing"):
        RunSimulation().execute(request)
