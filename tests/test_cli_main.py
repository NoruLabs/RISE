import sys
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
    assert "Thrust: 3905.640 N" in captured.out
    assert "Specific impulse: 221.258 s" in captured.out
    assert "Geometry:" in captured.out
    assert "Throat diameter:" in captured.out
    assert "Chamber diameter:" in captured.out
    assert "Chamber length:" in captured.out
    assert "Nozzle exit diameter:" in captured.out
    assert "Transient (0D chamber pressure):" in captured.out
    assert "Initial chamber pressure:" in captured.out
    assert "Final chamber pressure:" in captured.out
