import argparse
from pathlib import Path

from rise.application.use_cases.run_simulation import RunSimulation
from rise.infrastructure.config.engine_config_loader import load_engine_config
from rise.infrastructure.plotting.plotter import Plotter
from rise.interfaces.presenters.console_presenter import ConsolePresenter


def main() -> None:
    parser = argparse.ArgumentParser(description="RISE - Rocket Integrated Simulation Environment")
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the engine YAML config file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for plot output (default: output)",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip plot generation",
    )
    args = parser.parse_args()

    request = load_engine_config(args.config)
    result = RunSimulation().execute(request)
    output = ConsolePresenter().present(result)
    print(output)

    if not args.no_plots and result.transient is not None:
        plotter = Plotter(output_dir=str(args.output_dir))
        plotter.plot_all(result.transient)
        print(f"\nPlots saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
