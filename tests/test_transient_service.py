import pytest

from rise.domain.services.transient_service import (
    TransientState,
    _compute_exit_mach,
    compute_transient,
)


def test_transient_reaches_steady_state() -> None:
    """The 0D model should converge to the analytical steady-state pressure."""
    states = compute_transient(
        initial_chamber_pressure_pa=2_000_000.0,
        mass_flow_in_kg_s=1.8,
        ambient_pressure_pa=101_325.0,
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_volume_m3=0.0006096,
        gamma=1.22,
        molecular_weight_kg_per_kmol=22.0,
        chamber_temperature_k=3483.35,
        burn_time_s=10.0,
        time_step_s=0.001,
    )

    assert isinstance(states, list)
    assert len(states) > 0
    assert isinstance(states[0], TransientState)

    # Initial pressure should match input
    assert states[0].chamber_pressure_pa == pytest.approx(2_000_000.0)

    # Final pressure should be close to steady-state (~3.95 MPa for this case)
    assert states[-1].chamber_pressure_pa == pytest.approx(3_950_000.0, rel=0.02)

    # Mass flow should increase as pressure rises
    assert states[-1].mass_flow_kg_s > states[0].mass_flow_kg_s

    # Thrust should increase as pressure rises
    assert states[-1].thrust_n > states[0].thrust_n

    # No propellant tracking when not provided
    assert states[-1].remaining_propellant_kg == 0.0


def test_transient_with_short_burn_time() -> None:
    """A very short burn should still return at least the initial state."""
    states = compute_transient(
        initial_chamber_pressure_pa=2_000_000.0,
        mass_flow_in_kg_s=1.8,
        ambient_pressure_pa=101_325.0,
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_volume_m3=0.0006096,
        gamma=1.22,
        molecular_weight_kg_per_kmol=22.0,
        chamber_temperature_k=3483.35,
        burn_time_s=0.0,
        time_step_s=0.001,
    )

    assert len(states) == 1
    assert states[0].time_s == pytest.approx(0.0)
    assert states[0].chamber_pressure_pa == pytest.approx(2_000_000.0)


def test_transient_tracks_propellant_mass() -> None:
    """Propellant should deplete and stop the simulation when exhausted."""
    states = compute_transient(
        initial_chamber_pressure_pa=2_000_000.0,
        mass_flow_in_kg_s=1.8,
        ambient_pressure_pa=101_325.0,
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_volume_m3=0.0006096,
        gamma=1.22,
        molecular_weight_kg_per_kmol=22.0,
        chamber_temperature_k=3483.35,
        burn_time_s=10.0,
        time_step_s=0.001,
        propellant_mass_kg=3.6,  # 2 seconds of burn at 1.8 kg/s
    )

    assert len(states) > 0
    assert states[0].remaining_propellant_kg == pytest.approx(3.6)
    assert states[-1].remaining_propellant_kg == pytest.approx(0.0, abs=1e-6)
    # Burn should stop before 10 s
    assert states[-1].time_s < 5.0


def test_transient_stops_on_low_pressure() -> None:
    """Simulation should stop when chamber pressure drops below threshold."""
    states = compute_transient(
        initial_chamber_pressure_pa=2_000_000.0,
        mass_flow_in_kg_s=0.5,  # Low mass flow so pressure drops
        ambient_pressure_pa=101_325.0,
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_volume_m3=0.0006096,
        gamma=1.22,
        molecular_weight_kg_per_kmol=22.0,
        chamber_temperature_k=3483.35,
        burn_time_s=10.0,
        time_step_s=0.001,
        min_chamber_pressure_pa=1_500_000.0,
    )

    # Should stop before 10 s because pressure falls below threshold
    assert states[-1].time_s < 5.0
    # Last recorded pressure should be at or above the threshold
    assert states[-1].chamber_pressure_pa >= 1_500_000.0
    # With at least one step recorded, pressure should have decreased
    if len(states) > 1:
        assert states[-1].chamber_pressure_pa < states[0].chamber_pressure_pa


def test_transient_curve_structure() -> None:
    """The transient curve should have consistent time steps and one pressure per step."""
    burn_time = 5.0
    time_step = 0.001
    states = compute_transient(
        initial_chamber_pressure_pa=2_000_000.0,
        mass_flow_in_kg_s=1.8,
        ambient_pressure_pa=101_325.0,
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_volume_m3=0.0006096,
        gamma=1.22,
        molecular_weight_kg_per_kmol=22.0,
        chamber_temperature_k=3483.35,
        burn_time_s=burn_time,
        time_step_s=time_step,
        propellant_mass_kg=100.0,  # Plenty of propellant
    )

    # Time steps increase correctly
    assert len(states) > 1
    for i in range(1, len(states)):
        assert states[i].time_s > states[i - 1].time_s
        delta = states[i].time_s - states[i - 1].time_s
        assert delta == pytest.approx(time_step, abs=1e-9)

    # Pressure values are produced for each step
    assert len(states) == len([s for s in states if s.chamber_pressure_pa > 0])

    # Simulation stops at the burn time limit
    assert states[-1].time_s == pytest.approx(burn_time, abs=1e-9)

    # All expected fields are populated
    for s in states:
        assert s.mass_flow_kg_s > 0
        assert s.thrust_n > 0
        assert s.specific_impulse_s > 0
        assert s.remaining_propellant_kg > 0


def test_compute_exit_mach_raises_on_expansion_ratio_too_large() -> None:
    """An expansion ratio larger than the maximum for the given gamma should raise."""
    with pytest.raises(ValueError, match="too large"):
        _compute_exit_mach(expansion_ratio=1e9, gamma=1.22)


def test_transient_pressure_resets_to_zero_when_negative() -> None:
    """If pressure drops below zero during the Euler step, it should be clamped to zero."""
    states = compute_transient(
        initial_chamber_pressure_pa=100_000.0,
        mass_flow_in_kg_s=0.01,  # Very low inflow so pressure drops fast
        ambient_pressure_pa=101_325.0,
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_volume_m3=0.0006096,
        gamma=1.22,
        molecular_weight_kg_per_kmol=22.0,
        chamber_temperature_k=3483.35,
        burn_time_s=10.0,
        time_step_s=0.05,
    )

    # At least one state should have zero pressure after clamping
    assert any(s.chamber_pressure_pa == 0.0 for s in states)
