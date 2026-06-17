"""Unit tests for AltitudeService US Standard Atmosphere."""
from rise.domain.services.altitude_service import (
    ambient_pressure_pa,
    compute_altitude_sweep,
)


def test_sea_level_pressure():
    """Sea level should be 101325 Pa."""
    p = ambient_pressure_pa(0.0)
    assert abs(p - 101325.0) < 1.0


def test_11km_pressure():
    """At 11 km tropopause (ICAO std: ~22632 Pa)."""
    p = ambient_pressure_pa(11000.0)
    assert abs(p - 22632.0) < 50.0


def test_20km_pressure():
    """At 20 km stratosphere (ICAO std: ~5475 Pa)."""
    p = ambient_pressure_pa(20000.0)
    assert abs(p - 5474.89) < 10.0


def test_pressure_decreases_with_altitude():
    """Pressure must decrease monotonically with altitude."""
    alts = [0, 1000, 5000, 11000, 20000, 35000, 50000, 80000]
    pressures = [ambient_pressure_pa(h) for h in alts]
    for i in range(len(pressures) - 1):
        assert pressures[i] > pressures[i + 1]


def test_altitude_sweep_returns_one_point_per_altitude():
    sweep = compute_altitude_sweep(
        thrust_n_sea_level=10000.0,
        exit_area_m2=0.01,
        exit_pressure_pa=50000.0,
        mass_flow_kg_s=2.0,
        altitudes_m=[0.0, 10000.0, 20000.0],
    )
    assert len(sweep) == 3


def test_vacuum_thrust_higher_than_sea_level():
    """Thrust should increase as ambient pressure decreases."""
    sweep = compute_altitude_sweep(
        thrust_n_sea_level=10000.0,
        exit_area_m2=0.01,
        exit_pressure_pa=50000.0,
        mass_flow_kg_s=2.0,
        altitudes_m=[0.0, 80000.0],
    )
    assert sweep[1].thrust_n > sweep[0].thrust_n
