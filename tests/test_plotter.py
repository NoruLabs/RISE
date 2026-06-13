import os
import tempfile

from rise.application.dtos.transient_simulation_result import (
    TransientSimulationResult,
)
from rise.infrastructure.plotting.plotter import Plotter


def _make_sample_result() -> TransientSimulationResult:
    time_s = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    return TransientSimulationResult(
        time_s=time_s,
        chamber_pressure_pa=[
            2_000_000.0,
            2_500_000.0,
            3_000_000.0,
            3_500_000.0,
            4_000_000.0,
            4_500_000.0,
        ],
        mass_flow_kg_s=[1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        thrust_n=[1000.0, 1500.0, 2000.0, 2500.0, 3000.0, 3500.0],
        specific_impulse_s=[200.0, 210.0, 220.0, 230.0, 240.0, 250.0],
        remaining_propellant_kg=[10.0, 8.0, 6.0, 4.0, 2.0, 0.0],
        burn_time_s=5.0,
    )


def test_plotter_creates_pressure_plot() -> None:
    plotter = Plotter()
    result = _make_sample_result()
    with tempfile.TemporaryDirectory() as tmpdir:
        plotter.output_dir = tmpdir
        plotter.plot_pressure_time(result)
        assert os.path.exists(os.path.join(tmpdir, "chamber_pressure.png"))
        assert os.path.exists(os.path.join(tmpdir, "chamber_pressure.html"))
        assert os.path.getsize(os.path.join(tmpdir, "chamber_pressure.png")) > 0
        assert os.path.getsize(os.path.join(tmpdir, "chamber_pressure.html")) > 0


def test_plotter_creates_thrust_plot() -> None:
    plotter = Plotter()
    result = _make_sample_result()
    with tempfile.TemporaryDirectory() as tmpdir:
        plotter.output_dir = tmpdir
        plotter.plot_thrust_time(result)
        assert os.path.exists(os.path.join(tmpdir, "thrust.png"))
        assert os.path.exists(os.path.join(tmpdir, "thrust.html"))
        assert os.path.getsize(os.path.join(tmpdir, "thrust.png")) > 0
        assert os.path.getsize(os.path.join(tmpdir, "thrust.html")) > 0


def test_plotter_creates_mass_flow_plot() -> None:
    plotter = Plotter()
    result = _make_sample_result()
    with tempfile.TemporaryDirectory() as tmpdir:
        plotter.output_dir = tmpdir
        plotter.plot_mass_flow_time(result)
        assert os.path.exists(os.path.join(tmpdir, "mass_flow.png"))
        assert os.path.exists(os.path.join(tmpdir, "mass_flow.html"))
        assert os.path.getsize(os.path.join(tmpdir, "mass_flow.png")) > 0
        assert os.path.getsize(os.path.join(tmpdir, "mass_flow.html")) > 0


def test_plotter_creates_all_plots() -> None:
    plotter = Plotter()
    result = _make_sample_result()
    with tempfile.TemporaryDirectory() as tmpdir:
        plotter.output_dir = tmpdir
        plotter.plot_all(result)
        assert os.path.exists(os.path.join(tmpdir, "chamber_pressure.png"))
        assert os.path.exists(os.path.join(tmpdir, "chamber_pressure.html"))
        assert os.path.exists(os.path.join(tmpdir, "thrust.png"))
        assert os.path.exists(os.path.join(tmpdir, "thrust.html"))
        assert os.path.exists(os.path.join(tmpdir, "mass_flow.png"))
        assert os.path.exists(os.path.join(tmpdir, "mass_flow.html"))
