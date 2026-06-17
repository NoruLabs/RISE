"""Unit tests for NozzleFlowService isentropic relations."""
import pytest

from rise.domain.services.nozzle_flow_service import (
    area_ratio_to_mach,
    compute_nozzle_flow_profile,
    mach_to_pressure_ratio,
)


def test_area_ratio_to_mach_throat():
    """Area ratio of 1.0 should return Mach 1."""
    m = area_ratio_to_mach(1.0)
    assert abs(m - 1.0) < 1e-6


def test_area_ratio_to_mach_known_supersonic():
    """A/A* = 2.964 → Mach ≈ 2.5 (standard table value)."""
    m = area_ratio_to_mach(2.964, gamma=1.4, supersonic=True)
    assert abs(m - 2.5) < 0.01


def test_area_ratio_to_mach_known_subsonic():
    """A/A* = 2.964 subsonic branch → Mach < 1."""
    m = area_ratio_to_mach(2.964, gamma=1.4, supersonic=False)
    assert m < 1.0
    assert m > 0.0


def test_pressure_ratio_at_throat():
    """p/p0 at Mach 1 → critical pressure ratio (gamma=1.4)."""
    pr = mach_to_pressure_ratio(1.0, gamma=1.4)
    expected = (2.0 / 2.4) ** (1.4 / 0.4)
    assert abs(pr - expected) < 1e-9


def test_pressure_ratio_at_mach0():
    """p/p0 at Mach 0 should be 1.0."""
    pr = mach_to_pressure_ratio(0.0, gamma=1.4)
    assert abs(pr - 1.0) < 1e-9


def test_flow_profile_length():
    """Profile should return n_points + 1 entries."""
    profile = compute_nozzle_flow_profile(
        throat_area_m2=1e-4,
        exit_area_m2=6e-4,
        chamber_pressure_pa=5e6,
        chamber_length_m=0.1,
        converging_length_m=0.05,
        diverging_length_m=0.12,
        n_points=40,
    )
    assert len(profile) == 41


def test_flow_profile_pressure_decreases():
    """Pressure should be highest in chamber and decrease toward exit."""
    profile = compute_nozzle_flow_profile(
        throat_area_m2=1e-4,
        exit_area_m2=6e-4,
        chamber_pressure_pa=5e6,
        chamber_length_m=0.1,
        converging_length_m=0.05,
        diverging_length_m=0.12,
        n_points=40,
    )
    pressures = [p.local_pressure_pa for p in profile]
    assert pressures[0] >= pressures[-1]
