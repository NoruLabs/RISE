import math
from dataclasses import dataclass


@dataclass(slots=True)
class TransientState:
    time_s: float
    chamber_pressure_pa: float
    mass_flow_kg_s: float
    thrust_n: float
    specific_impulse_s: float


def _compute_exit_mach(expansion_ratio: float, gamma: float) -> float:
    """Solve the area-Mach relation for the supersonic exit Mach number."""

    def _area_mach(M: float) -> float:
        return (1.0 / M) * (
            (2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * M**2.0)
        ) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0)))

    low, high = 1.0, 20.0
    if _area_mach(high) < expansion_ratio:
        raise ValueError(
            f"Expansion ratio {expansion_ratio} too large for gamma={gamma}"
        )

    for _ in range(100):
        mid = (low + high) / 2.0
        area = _area_mach(mid)
        if abs(area - expansion_ratio) < 1e-7:
            return mid
        if area < expansion_ratio:
            low = mid
        else:
            high = mid

    return (low + high) / 2.0


def compute_transient(
    initial_chamber_pressure_pa: float,
    mass_flow_in_kg_s: float,
    ambient_pressure_pa: float,
    throat_area_m2: float,
    exit_area_m2: float,
    chamber_volume_m3: float,
    gamma: float,
    molecular_weight_kg_per_kmol: float,
    chamber_temperature_k: float,
    burn_time_s: float,
    time_step_s: float,
) -> list[TransientState]:
    """0D chamber pressure transient with isentropic nozzle relations."""

    R_universal = 8314.0  # J/(kmol·K)
    R = R_universal / molecular_weight_kg_per_kmol  # J/(kg·K)
    g0 = 9.80665

    expansion_ratio = exit_area_m2 / throat_area_m2
    M_e = _compute_exit_mach(expansion_ratio, gamma)

    # Isentropic temperature and pressure ratios (constant)
    T_e = chamber_temperature_k / (1.0 + (gamma - 1.0) / 2.0 * M_e**2.0)
    P_e_over_P_c = (1.0 + (gamma - 1.0) / 2.0 * M_e**2.0) ** (
        -gamma / (gamma - 1.0)
    )
    V_e = M_e * math.sqrt(gamma * R * T_e)

    # Choked flow coefficient: m_dot_out = coeff * P_c / sqrt(T_c)
    coeff = (
        throat_area_m2
        * math.sqrt(gamma / R)
        * (1.0 + (gamma - 1.0) / 2.0)
        ** (-(gamma + 1.0) / (2.0 * (gamma - 1.0)))
    )

    # Linear ODE coefficients: dP/dt = b - a*P_c
    coeff_press = (R * chamber_temperature_k) / chamber_volume_m3
    a = coeff_press * coeff / math.sqrt(chamber_temperature_k)
    b = coeff_press * mass_flow_in_kg_s

    states: list[TransientState] = []
    P_c = initial_chamber_pressure_pa
    t = 0.0

    while t <= burn_time_s + 1e-9:
        m_dot_out = coeff * P_c / math.sqrt(chamber_temperature_k)

        P_e = P_c * P_e_over_P_c
        pressure_thrust = (P_e - ambient_pressure_pa) * exit_area_m2
        thrust = m_dot_out * V_e + pressure_thrust
        isp = thrust / (m_dot_out * g0) if m_dot_out > 0 else 0.0

        states.append(
            TransientState(
                time_s=t,
                chamber_pressure_pa=P_c,
                mass_flow_kg_s=m_dot_out,
                thrust_n=thrust,
                specific_impulse_s=isp,
            )
        )

        # Implicit Euler: unconditionally stable for linear ODE
        P_c = (P_c + time_step_s * b) / (1.0 + time_step_s * a)
        t += time_step_s

    return states
