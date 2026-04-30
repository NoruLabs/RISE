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