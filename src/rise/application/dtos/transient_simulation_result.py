from dataclasses import dataclass


@dataclass(slots=True)
class TransientSimulationResult:
    time_s: list[float]
    chamber_pressure_pa: list[float]
    mass_flow_kg_s: list[float]
    thrust_n: list[float]
    specific_impulse_s: list[float]
    burn_time_s: float
