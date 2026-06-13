import math
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GeometryResult:
    throat_diameter_m: float
    throat_radius_m: float
    chamber_volume_m3: float
    chamber_diameter_m: float
    chamber_length_m: float
    converging_length_m: float
    diverging_length_m: float
    exit_diameter_m: float
    expansion_ratio: float


def compute_geometry(
    throat_area_m2: float,
    exit_area_m2: float,
    characteristic_length_m: float,
    contraction_ratio: float,
    convergent_half_angle_deg: float,
    divergent_half_angle_deg: float,
) -> GeometryResult:
    throat_diameter_m = 2.0 * math.sqrt(throat_area_m2 / math.pi)
    throat_radius_m = throat_diameter_m / 2.0
    exit_diameter_m = 2.0 * math.sqrt(exit_area_m2 / math.pi)
    chamber_diameter_m = math.sqrt(contraction_ratio) * throat_diameter_m
    chamber_volume_m3 = characteristic_length_m * throat_area_m2
    chamber_length_m = chamber_volume_m3 / (
        math.pi * (chamber_diameter_m / 2.0) ** 2
    )

    convergent_half_angle_rad = math.radians(convergent_half_angle_deg)
    divergent_half_angle_rad = math.radians(divergent_half_angle_deg)

    converging_length_m = (
        (chamber_diameter_m - throat_diameter_m)
        / (2.0 * math.tan(convergent_half_angle_rad))
    )
    diverging_length_m = (
        (exit_diameter_m - throat_diameter_m)
        / (2.0 * math.tan(divergent_half_angle_rad))
    )

    return GeometryResult(
        throat_diameter_m=throat_diameter_m,
        throat_radius_m=throat_radius_m,
        chamber_volume_m3=chamber_volume_m3,
        chamber_diameter_m=chamber_diameter_m,
        chamber_length_m=chamber_length_m,
        converging_length_m=converging_length_m,
        diverging_length_m=diverging_length_m,
        exit_diameter_m=exit_diameter_m,
        expansion_ratio=exit_area_m2 / throat_area_m2,
    )
