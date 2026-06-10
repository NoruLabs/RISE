from rise.application.dtos.simulation_input import SimulationInput
from rise.application.dtos.simulation_result import SimulationResult
from rise.application.dtos.transient_simulation_result import (
    TransientSimulationResult,
)
from rise.domain.entities.engine import Engine
from rise.domain.entities.nozzle import Nozzle
from rise.domain.services.geometry_service import compute_geometry
from rise.domain.services.transient_service import compute_transient
from rise.domain.value_objects.operating_point import OperatingPoint


class RunSimulation:
    def execute(self, request: SimulationInput) -> SimulationResult:
        nozzle = Nozzle(
            throat_area_m2=request.throat_area_m2,
            exit_area_m2=request.exit_area_m2,
        )

        operating_point = OperatingPoint(
            chamber_pressure_pa=request.chamber_pressure_pa,
            ambient_pressure_pa=request.ambient_pressure_pa,
            mass_flow_kg_s=request.mass_flow_kg_s,
            exit_velocity_m_s=request.exit_velocity_m_s,
            exit_pressure_pa=request.exit_pressure_pa,
        )

        engine = Engine(
            name=request.engine_name,
            nozzle=nozzle,
            operating_point=operating_point,
        )

        engine.validate()

        geometry = compute_geometry(
            throat_area_m2=request.throat_area_m2,
            exit_area_m2=request.exit_area_m2,
            characteristic_length_m=request.characteristic_length_m,
            contraction_ratio=request.contraction_ratio,
            convergent_half_angle_deg=request.convergent_half_angle_deg,
            divergent_half_angle_deg=request.divergent_half_angle_deg,
        )

        transient_result = None
        if request.burn_time_s is not None and request.time_step_s is not None:
            initial_p = (
                request.initial_chamber_pressure_pa
                if request.initial_chamber_pressure_pa is not None
                else request.chamber_pressure_pa
            )
            states = compute_transient(
                initial_chamber_pressure_pa=initial_p,
                mass_flow_in_kg_s=request.mass_flow_kg_s,
                ambient_pressure_pa=request.ambient_pressure_pa,
                throat_area_m2=request.throat_area_m2,
                exit_area_m2=request.exit_area_m2,
                chamber_volume_m3=geometry.chamber_volume_m3,
                gamma=request.gamma,
                molecular_weight_kg_per_kmol=request.molecular_weight_kg_per_kmol,
                chamber_temperature_k=request.chamber_temperature_k,
                burn_time_s=request.burn_time_s,
                time_step_s=request.time_step_s,
                propellant_mass_kg=request.propellant_mass_kg,
                min_chamber_pressure_pa=request.min_chamber_pressure_pa,
            )
            transient_result = TransientSimulationResult(
                time_s=[s.time_s for s in states],
                chamber_pressure_pa=[s.chamber_pressure_pa for s in states],
                mass_flow_kg_s=[s.mass_flow_kg_s for s in states],
                thrust_n=[s.thrust_n for s in states],
                specific_impulse_s=[s.specific_impulse_s for s in states],
                remaining_propellant_kg=[s.remaining_propellant_kg for s in states],
                burn_time_s=request.burn_time_s,
            )

        return SimulationResult(
            engine_name=engine.name,
            expansion_ratio=engine.nozzle.expansion_ratio,
            thrust_n=engine.compute_thrust(),
            specific_impulse_s=engine.compute_specific_impulse(),
            geometry=geometry,
            transient=transient_result,
        )