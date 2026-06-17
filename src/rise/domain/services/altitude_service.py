"""AltitudeService — US Standard Atmosphere 1976 and altitude performance.

Pure domain service: only numbers in, only numbers out.
No YAML, no HTTP, no file I/O.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


_G0 = 9.80665  # m/s^2
_R_AIR = 287.058  # J/(kg·K)

# US Standard Atmosphere 1976 layer table
# Each entry: (base_altitude_m, base_temp_k, lapse_rate_k_per_m, base_pressure_pa)
_LAYERS = [
    (0.0,      288.15, -0.0065, 101325.0),
    (11000.0,  216.65,  0.0,    22632.1),
    (20000.0,  216.65,  0.001,  5474.89),
    (32000.0,  228.65,  0.0028, 868.019),
    (47000.0,  270.65,  0.0,    110.906),
    (51000.0,  270.65, -0.0028, 66.9389),
    (71000.0,  214.65, -0.002,  3.95642),
    (86000.0,  186.87,  0.0,    0.3734),
]


def ambient_pressure_pa(altitude_m: float) -> float:
    """Return ambient pressure in Pa at given altitude (m) using US Std Atm 1976."""
    if altitude_m < 0.0:
        return _LAYERS[0][3]

    layer = _LAYERS[0]
    for entry in _LAYERS[1:]:
        if altitude_m >= entry[0]:
            layer = entry
        else:
            break

    h0, t0, lr, p0 = layer
    delta_h = altitude_m - h0

    if abs(lr) < 1e-10:
        # Isothermal layer
        return p0 * math.exp(-_G0 * delta_h / (_R_AIR * t0))
    else:
        # Gradient layer
        return p0 * ((t0 + lr * delta_h) / t0) ** (-_G0 / (lr * _R_AIR))


@dataclass(slots=True, frozen=True)
class AltitudePerformancePoint:
    altitude_m: float
    ambient_pressure_pa: float
    thrust_n: float
    specific_impulse_s: float


def compute_altitude_sweep(
    thrust_n_sea_level: float,
    exit_area_m2: float,
    exit_pressure_pa: float,
    mass_flow_kg_s: float,
    altitudes_m: list[float],
) -> list[AltitudePerformancePoint]:
    """Compute thrust and Isp at each altitude.

    Thrust = F_sl + (p_exit - p_amb) * A_exit
    The momentum term is constant; only the pressure thrust term changes.
    """
    # Sea-level ambient for reference
    p_amb_sl = ambient_pressure_pa(0.0)
    # Momentum thrust + pressure thrust at sea level
    momentum_thrust = thrust_n_sea_level - (exit_pressure_pa - p_amb_sl) * exit_area_m2

    results: list[AltitudePerformancePoint] = []
    for alt in altitudes_m:
        p_amb = ambient_pressure_pa(alt)
        thrust = momentum_thrust + (exit_pressure_pa - p_amb) * exit_area_m2
        isp = thrust / (mass_flow_kg_s * _G0) if mass_flow_kg_s > 0 else 0.0
        results.append(AltitudePerformancePoint(
            altitude_m=alt,
            ambient_pressure_pa=p_amb,
            thrust_n=thrust,
            specific_impulse_s=isp,
        ))
    return results
