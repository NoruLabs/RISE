from pathlib import Path

from rise.application.use_cases.run_simulation import RunSimulation
from rise.infrastructure.config.engine_config_loader import load_engine_config
from rise.interfaces.presenters.console_presenter import ConsolePresenter


def main() -> None:
    config_path = Path("configs/engines/pressure_fed_test.yaml")
    request = load_engine_config(config_path)

    use_case = RunSimulation()
    result = use_case.execute(request)

    presenter = ConsolePresenter()
    presenter.present(result)


if __name__ == "__main__":
    main()
