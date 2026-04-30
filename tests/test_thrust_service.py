import pytest

from rise.domain.entities.nozzle import Nozzle
from rise.domain.value_objects.operating_point import OperatingPoint
from rise.domain.services.thrust_service import (
    compute_specific_impulse,
    compute_thrust,
)


def test_compute_thrust_matches_expected_value() -> None:
    nozzle = Nozzle(
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
    )

    operating_point = OperatingPoint(
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=1.8,
        exit_velocity_m_s=2_200.0,
        exit_pressure_pa=90_000.0,
    )

    thrust = compute_thrust(nozzle, operating_point)

    assert thrust == pytest.approx(3905.64)


def test_compute_specific_impulse_matches_expected_value() -> None:
    nozzle = Nozzle(
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
    )

    operating_point = OperatingPoint(
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=1.8,
        exit_velocity_m_s=2_200.0,
        exit_pressure_pa=90_000.0,
    )

    isp = compute_specific_impulse(nozzle, operating_point)

    assert isp == pytest.approx(221.258, abs=1e-3)


def test_nozzle_expansion_ratio_is_computed_correctly() -> None:
    nozzle = Nozzle(
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
    )

    assert nozzle.expansion_ratio == pytest.approx(6.0)
    
def test_nozzle_validate_raises_when_throat_area_is_not_positive() -> None:
    nozzle = Nozzle(
        throat_area_m2=0.0,
        exit_area_m2=0.0048,
    )

    with pytest.raises(ValueError, match="throat_area_m2 must be greater than 0"):
        nozzle.validate()


def test_nozzle_validate_raises_when_exit_area_is_smaller_than_throat() -> None:
    nozzle = Nozzle(
        throat_area_m2=0.002,
        exit_area_m2=0.001,
    )

    with pytest.raises(ValueError, match="exit_area_m2 must be >= throat_area_m2"):
        nozzle.validate()


def test_operating_point_validate_raises_when_mass_flow_is_not_positive() -> None:
    operating_point = OperatingPoint(
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=0.0,
        exit_velocity_m_s=2_200.0,
        exit_pressure_pa=90_000.0,
    )

    with pytest.raises(ValueError, match="mass_flow_kg_s must be greater than 0"):
        operating_point.validate()


def test_operating_point_validate_raises_when_ambient_pressure_is_negative() -> None:
    operating_point = OperatingPoint(
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=-1.0,
        mass_flow_kg_s=1.8,
        exit_velocity_m_s=2_200.0,
        exit_pressure_pa=90_000.0,
    )

    with pytest.raises(ValueError, match="ambient_pressure_pa cannot be negative"):
        operating_point.validate()