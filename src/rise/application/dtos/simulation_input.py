from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class SimulationInput:
    engine_name: str
    throat_area_m2: float
    exit_area_m2: float
    chamber_pressure_pa: float
    ambient_pressure_pa: float
    mass_flow_kg_s: float
    characteristic_length_m: float
    contraction_ratio: float
    convergent_half_angle_deg: float
    divergent_half_angle_deg: float
    nozzle_length_method: str
    oxidizer: str | None = None
    fuel: str | None = None
    gamma: float | None = None
    molecular_weight_kg_per_kmol: float | None = None
    chamber_temperature_k: float | None = None
    exit_velocity_m_s: float | None = None
    exit_pressure_pa: float | None = None
    initial_chamber_pressure_pa: float | None = None
    burn_time_s: float | None = None
    time_step_s: float | None = None
    propellant_mass_kg: float | None = None
    min_chamber_pressure_pa: float | None = None
    mixture_ratio: float | None = None
    mass_flow_decay_model: str | None = None
    # Stage 20: efficiency factors.  Default 1.0 — no breaking change.
    combustion_efficiency: float = 1.0
    nozzle_efficiency: float = 1.0
    # Stage 20: optional altitude sweep
    altitude_sweep_m: list[float] | None = None
