import pytest

from rise.domain.services.geometry_service import GeometryResult, compute_geometry


def test_compute_geometry_returns_correct_values() -> None:
    result = compute_geometry(
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        characteristic_length_m=0.762,
        contraction_ratio=5.0,
        convergent_half_angle_deg=30.0,
        divergent_half_angle_deg=15.0,
    )

    assert isinstance(result, GeometryResult)
    assert result.throat_diameter_m == pytest.approx(0.0319154, abs=1e-6)
    assert result.throat_radius_m == pytest.approx(0.0159577, abs=1e-6)
    assert result.exit_diameter_m == pytest.approx(0.0781764, abs=1e-6)
    assert result.chamber_diameter_m == pytest.approx(0.0713650, abs=1e-6)
    assert result.chamber_volume_m3 == pytest.approx(0.0006096, abs=1e-6)
    assert result.chamber_length_m == pytest.approx(0.1524, abs=1e-6)
    assert result.converging_length_m == pytest.approx(0.0341643, abs=1e-6)
    assert result.diverging_length_m == pytest.approx(0.0863242, abs=1e-6)
    assert result.expansion_ratio == pytest.approx(6.0)
