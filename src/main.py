from rise.domain.entities.nozzle import Nozzle
from rise.domain.value_objects.operating_point import OperatingPoint
from rise.domain.services.thrust_service import (
    compute_specific_impulse,
    compute_thrust,
)


def main() -> None:
    nozzle = Nozzle(
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
    )

    operating_point = OperatingPoint(
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=1.8,
        exit_velocity_m_s=2_200.0,
        exit_pressure_pa=90_000.0,
    )

    thrust_n = compute_thrust(nozzle, operating_point)
    isp_s = compute_specific_impulse(nozzle, operating_point)

    print("RISE - Rocket Integrated Simulation Environment")
    print(f"Expansion ratio: {nozzle.expansion_ratio:.3f}")
    print(f"Thrust: {thrust_n:.3f} N")
    print(f"Specific impulse: {isp_s:.3f} s")


if __name__ == "__main__":
    main()