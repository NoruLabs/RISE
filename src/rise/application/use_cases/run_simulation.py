from rise.application.dtos.simulation_input import SimulationInput
from rise.application.dtos.simulation_result import SimulationResult
from rise.domain.entities.engine import Engine
from rise.domain.entities.nozzle import Nozzle
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

        return SimulationResult(
            engine_name=engine.name,
            expansion_ratio=engine.nozzle.expansion_ratio,
            thrust_n=engine.compute_thrust(),
            specific_impulse_s=engine.compute_specific_impulse(),
        )