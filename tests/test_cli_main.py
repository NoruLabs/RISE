import os
import sys
import tempfile
from pathlib import Path

import pytest

from rise.interfaces.cli.main import main


def test_cli_main_runs_simulation_successfully(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = Path("configs/engines/pressure_fed_test.yaml")
    monkeypatch.setattr(sys, "argv", ["rise", "--config", str(config_path)])

    main()

    captured = capsys.readouterr()
    assert "RISE - Rocket Integrated Simulation Environment" in captured.out
    assert "Engine: pressure-fed-test" in captured.out
    assert "Expansion ratio: 6.000" in captured.out
    assert "Thrust: 6937.820 N" in captured.out
    assert "Specific impulse: 393.034 s" in captured.out
    assert "Geometry:" in captured.out
    assert "Throat diameter:" in captured.out
    assert "Chamber diameter:" in captured.out
    assert "Chamber length:" in captured.out
    assert "Nozzle exit diameter:" in captured.out
    assert "Transient (0D chamber pressure):" in captured.out
    assert "Initial pressure:" in captured.out
    assert "Peak pressure:" in captured.out
    assert "Final pressure:" in captured.out
    assert "Average thrust:" in captured.out
    assert "Burn time:" in captured.out


def test_cli_main_generates_plots(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI should generate plot files after simulation."""
    config_path = Path("configs/engines/pressure_fed_test.yaml")
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "plots"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rise",
                "--config",
                str(config_path),
                "--output-dir",
                str(output_dir),
            ],
        )

        main()

        # Verify PNG files are created and non-empty
        assert os.path.exists(output_dir / "chamber_pressure.png")
        assert os.path.exists(output_dir / "thrust.png")
        assert os.path.exists(output_dir / "mass_flow.png")
        assert os.path.getsize(output_dir / "chamber_pressure.png") > 0
        assert os.path.getsize(output_dir / "thrust.png") > 0
        assert os.path.getsize(output_dir / "mass_flow.png") > 0

        # Verify HTML files are created and non-empty
        assert os.path.exists(output_dir / "chamber_pressure.html")
        assert os.path.exists(output_dir / "thrust.html")
        assert os.path.exists(output_dir / "mass_flow.html")
        assert os.path.getsize(output_dir / "chamber_pressure.html") > 0
        assert os.path.getsize(output_dir / "thrust.html") > 0
        assert os.path.getsize(output_dir / "mass_flow.html") > 0

        # Verify CLI reports the output location
        captured = capsys.readouterr()
        assert "Plots saved to" in captured.out


def test_cli_main_no_plots_flag(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--no-plots should skip plot generation."""
    config_path = Path("configs/engines/pressure_fed_test.yaml")
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "plots"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "rise",
                "--config",
                str(config_path),
                "--output-dir",
                str(output_dir),
                "--no-plots",
            ],
        )

        main()

        # No plots should be generated
        assert not os.path.exists(output_dir / "chamber_pressure.png")
        assert not os.path.exists(output_dir / "thrust.png")
        assert not os.path.exists(output_dir / "mass_flow.png")

        # CLI should not mention plot output
        captured = capsys.readouterr()
        assert "Plots saved to" not in captured.out
