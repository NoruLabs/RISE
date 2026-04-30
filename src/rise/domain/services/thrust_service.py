from rise.domain.entities.nozzle import Nozzle
from rise.domain.value_objects.operating_point import OperatingPoint

STANDARD_GRAVITY_M_S2 = 9.80665


def compute_thrust(nozzle: Nozzle, operating_point: OperatingPoint) -> float:
    nozzle.validate()
    operating_point.validate()

    momentum_thrust = (
        operating_point.mass_flow_kg_s * operating_point.exit_velocity_m_s
    )
    pressure_thrust = (
        operating_point.exit_pressure_pa - operating_point.ambient_pressure_pa
    ) * nozzle.exit_area_m2

    return momentum_thrust + pressure_thrust


def compute_specific_impulse(
    nozzle: Nozzle,
    operating_point: OperatingPoint,
) -> float:
    thrust_n = compute_thrust(nozzle, operating_point)
    return thrust_n / (operating_point.mass_flow_kg_s * STANDARD_GRAVITY_M_S2)