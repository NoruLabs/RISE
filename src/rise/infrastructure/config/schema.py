from pydantic import BaseModel, Field, model_validator


class EngineConfigSchema(BaseModel):
    """Pydantic schema for engine YAML configuration files.

    Validates every field expected from the YAML before conversion
    to the application SimulationInput DTO.
    """

    # Required fields
    name: str = Field(..., description="Engine identifier")
    throat_area_m2: float = Field(..., gt=0, description="Throat area in square meters")
    exit_area_m2: float = Field(..., gt=0, description="Exit area in square meters")
    chamber_pressure_pa: float = Field(..., gt=0, description="Chamber pressure in Pa")
    ambient_pressure_pa: float = Field(..., ge=0, description="Ambient pressure in Pa")
    mass_flow_kg_s: float = Field(..., gt=0, description="Mass flow rate in kg/s")
    characteristic_length_m: float = Field(..., gt=0, description="Characteristic length L* in m")
    contraction_ratio: float = Field(..., gt=0, description="Chamber-to-throat area ratio")
    convergent_half_angle_deg: float = Field(..., gt=0, description="Convergent half-angle in degrees")
    divergent_half_angle_deg: float = Field(..., gt=0, description="Divergent half-angle in degrees")
    nozzle_length_method: str = Field(..., description="Nozzle length calculation method")

    # Optional propellant / chemistry fields
    oxidizer: str | None = Field(default=None, description="Oxidizer propellant name")
    fuel: str | None = Field(default=None, description="Fuel propellant name")
    mixture_ratio: float | None = Field(default=None, gt=0, description="O/F mixture ratio")
    gamma: float | None = Field(default=None, gt=0, description="Ratio of specific heats")
    molecular_weight_kg_per_kmol: float | None = Field(
        default=None, gt=0, description="Molecular weight in kg/kmol"
    )
    chamber_temperature_k: float | None = Field(
        default=None, gt=0, description="Chamber temperature in K"
    )
    exit_velocity_m_s: float | None = Field(
        default=None, gt=0, description="Exit velocity in m/s"
    )
    exit_pressure_pa: float | None = Field(
        default=None, ge=0, description="Exit pressure in Pa"
    )

    # Optional transient fields
    initial_chamber_pressure_pa: float | None = Field(
        default=None, gt=0, description="Initial chamber pressure for transient in Pa"
    )
    burn_time_s: float | None = Field(
        default=None, gt=0, description="Total burn time in seconds"
    )
    time_step_s: float | None = Field(
        default=None, gt=0, description="Integration time step in seconds"
    )
    propellant_mass_kg: float | None = Field(
        default=None, ge=0, description="Initial propellant mass in kg"
    )
    min_chamber_pressure_pa: float | None = Field(
        default=None, ge=0, description="Minimum pressure cutoff for transient in Pa"
    )
    mass_flow_decay_model: str | None = Field(
        default=None, description="Mass flow decay model name"
    )

    @model_validator(mode="after")
    def check_exit_larger_than_throat(self) -> "EngineConfigSchema":
        """Cross-field validation: exit area must be >= throat area."""
        if self.exit_area_m2 < self.throat_area_m2:
            raise ValueError("exit_area_m2 must be >= throat_area_m2")
        return self

    def to_simulation_input(self) -> dict:
        """Return a plain dict compatible with SimulationInput."""
        return {
            "engine_name": self.name,
            "throat_area_m2": self.throat_area_m2,
            "exit_area_m2": self.exit_area_m2,
            "chamber_pressure_pa": self.chamber_pressure_pa,
            "ambient_pressure_pa": self.ambient_pressure_pa,
            "mass_flow_kg_s": self.mass_flow_kg_s,
            "characteristic_length_m": self.characteristic_length_m,
            "contraction_ratio": self.contraction_ratio,
            "convergent_half_angle_deg": self.convergent_half_angle_deg,
            "divergent_half_angle_deg": self.divergent_half_angle_deg,
            "nozzle_length_method": self.nozzle_length_method,
            "oxidizer": self.oxidizer,
            "fuel": self.fuel,
            "gamma": self.gamma,
            "molecular_weight_kg_per_kmol": self.molecular_weight_kg_per_kmol,
            "chamber_temperature_k": self.chamber_temperature_k,
            "exit_velocity_m_s": self.exit_velocity_m_s,
            "exit_pressure_pa": self.exit_pressure_pa,
            "initial_chamber_pressure_pa": self.initial_chamber_pressure_pa,
            "burn_time_s": self.burn_time_s,
            "time_step_s": self.time_step_s,
            "propellant_mass_kg": self.propellant_mass_kg,
            "min_chamber_pressure_pa": self.min_chamber_pressure_pa,
            "mixture_ratio": self.mixture_ratio,
            "mass_flow_decay_model": self.mass_flow_decay_model,
        }
