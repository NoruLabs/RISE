from dataclasses import dataclass


@dataclass(slots=True)
class SimulationInput:
    engine_name: str
    throat_area_m2: float
    exit_area_m2: float
    chamber_pressure_pa: float
    ambient_pressure_pa: float
    mass_flow_kg_s: float
    exit_velocity_m_s: float
    exit_pressure_pa: float
    oxidizer: str
    fuel: str
    gamma: float
    molecular_weight_kg_per_kmol: float
    chamber_temperature_k: float
    characteristic_length_m: float
    contraction_ratio: float
    convergent_half_angle_deg: float
    divergent_half_angle_deg: float
    nozzle_length_method: str
    burn_time_s: float | None = None
    time_step_s: float | None = None