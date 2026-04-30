from rise.domain.entities.engine import Engine
from rise.domain.entities.nozzle import Nozzle
from rise.domain.value_objects.operating_point import OperatingPoint


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

    engine = Engine(
        name="pressure-fed-test",
        nozzle=nozzle,
        operating_point=operating_point,
    )

    engine.validate()
    thrust = engine.compute_thrust()
    isp = engine.compute_specific_impulse()

    print("RISE - Rocket Integrated Simulation Environment")
    print(f"Engine: {engine.name}")
    print(f"Expansion ratio: {engine.nozzle.expansion_ratio:.3f}")
    print(f"Thrust: {thrust:.3f} N")
    print(f"Specific impulse: {isp:.3f} s")


if __name__ == "__main__":
    main()
