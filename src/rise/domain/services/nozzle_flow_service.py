"""NozzleFlowService — isentropic flow relations.

Pure domain math: no I/O, no side effects, no external dependencies.
All functions take numbers and return numbers.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class NozzleFlowPoint:
    """Isentropic flow state at one axial station."""

    axial_position_m: float
    area_ratio: float
    mach: float
    pressure_ratio: float  # p/p0
    local_pressure_pa: float


def area_ratio_to_mach(area_ratio: float, gamma: float = 1.4, supersonic: bool = True) -> float:
    """Solve the isentropic area-Mach relation for Mach given A/A*.

    Uses Newton-Raphson iteration.  Converges in < 20 iterations for all
    physically meaningful inputs.
    """
    if area_ratio <= 1.0:
        return 1.0  # throat
    gp1 = gamma + 1.0
    gm1 = gamma - 1.0
    exponent = gp1 / (2.0 * gm1)

    def f(m: float) -> float:
        inner = (2.0 + gm1 * m * m) / gp1
        return (1.0 / m) * (inner ** exponent) - area_ratio

    def df(m: float) -> float:
        inner = (2.0 + gm1 * m * m) / gp1
        dlog = (2.0 * gm1 * m) / (gp1 * inner)
        return -(1.0 / m**2) * (inner**exponent) + (1.0 / m) * exponent * (inner**exponent) * dlog

    m = 2.0 if supersonic else 0.5
    for _ in range(50):
        fm = f(m)
        if abs(fm) < 1e-10:
            break
        dm = df(m)
        if dm == 0.0:
            break
        m -= fm / dm
        m = max(m, 1e-6)
    return m


def mach_to_pressure_ratio(mach: float, gamma: float = 1.4) -> float:
    """Return p/p0 given Mach number (isentropic)."""
    gm1 = gamma - 1.0
    return (1.0 + 0.5 * gm1 * mach**2) ** (-gamma / gm1)


def compute_nozzle_flow_profile(
    throat_area_m2: float,
    exit_area_m2: float,
    chamber_pressure_pa: float,
    chamber_length_m: float,
    converging_length_m: float,
    diverging_length_m: float,
    gamma: float = 1.4,
    n_points: int = 80,
) -> list[NozzleFlowPoint]:
    """Return a list of NozzleFlowPoint across the full nozzle length.

    Splits into converging (subsonic) + diverging (supersonic) halves.
    The total axial span: 0 at chamber inlet → end of nozzle.
    """
    total_length = chamber_length_m + converging_length_m + diverging_length_m
    throat_x = chamber_length_m + converging_length_m
    points: list[NozzleFlowPoint] = []

    for i in range(n_points + 1):
        x = total_length * i / n_points

        if x <= chamber_length_m:
            mach = 0.1
            ar = 1e6
        elif x <= throat_x:
            frac = (x - chamber_length_m) / converging_length_m if converging_length_m > 0 else 1.0
            chamber_area = throat_area_m2 * (exit_area_m2 / throat_area_m2)
            area = chamber_area + (throat_area_m2 - chamber_area) * frac
            ar = area / throat_area_m2
            mach = area_ratio_to_mach(max(ar, 1.0), gamma, supersonic=False)
        else:
            frac = (x - throat_x) / diverging_length_m if diverging_length_m > 0 else 1.0
            area = throat_area_m2 + (exit_area_m2 - throat_area_m2) * frac
            ar = area / throat_area_m2
            mach = area_ratio_to_mach(max(ar, 1.0), gamma, supersonic=True)

        p_ratio = mach_to_pressure_ratio(mach, gamma)
        local_p = chamber_pressure_pa * p_ratio
        points.append(NozzleFlowPoint(
            axial_position_m=x,
            area_ratio=ar,
            mach=mach,
            pressure_ratio=p_ratio,
            local_pressure_pa=local_p,
        ))
    return points
