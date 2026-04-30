from rise.application.dtos.simulation_input import SimulationInput
from rise.application.use_cases.run_simulation import RunSimulation
from rise.interfaces.presenters.console_presenter import ConsolePresenter


def main() -> None:
    request = SimulationInput(
        engine_name="pressure-fed-test",
        throat_area_m2=0.0008,
        exit_area_m2=0.0048,
        chamber_pressure_pa=2_000_000.0,
        ambient_pressure_pa=101_325.0,
        mass_flow_kg_s=1.8,
        exit_velocity_m_s=2_200.0,
        exit_pressure_pa=90_000.0,
    )

    use_case = RunSimulation()
    result = use_case.execute(request)

    presenter = ConsolePresenter()
    presenter.present(result)


if __name__ == "__main__":
    main()
