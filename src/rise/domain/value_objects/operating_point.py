from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class OperatingPoint:
    chamber_pressure_pa: float
    ambient_pressure_pa: float
    mass_flow_kg_s: float
    exit_velocity_m_s: float
    exit_pressure_pa: float

    def validate(self) -> None:
        if self.chamber_pressure_pa <= 0:
            raise ValueError("chamber_pressure_pa must be greater than 0")

        if self.ambient_pressure_pa < 0:
            raise ValueError("ambient_pressure_pa cannot be negative")

        if self.mass_flow_kg_s <= 0:
            raise ValueError("mass_flow_kg_s must be greater than 0")

        if self.exit_velocity_m_s <= 0:
            raise ValueError("exit_velocity_m_s must be greater than 0")

        if self.exit_pressure_pa < 0:
            raise ValueError("exit_pressure_pa cannot be negative")