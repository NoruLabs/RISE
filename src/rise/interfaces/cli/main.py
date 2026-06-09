from pathlib import Path
import argparse

from rise.application.use_cases.run_simulation import RunSimulation
from rise.infrastructure.config.engine_config_loader import load_engine_config
from rise.interfaces.presenters.console_presenter import ConsolePresenter


def main() -> None:
    parser = argparse.ArgumentParser(description="RISE - Rocket Integrated Simulation Environment")
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the engine YAML config file",
    )
    args = parser.parse_args()

    request = load_engine_config(args.config)
    result = RunSimulation().execute(request)
    output = ConsolePresenter().present(result)
    print(output)


if __name__ == "__main__":
    main()
